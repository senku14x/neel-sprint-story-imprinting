"""Item 6: health-panel noise floor. Is the parent-vs-parent null exact because Tinker is deterministic, or only because
the reference and 'model' passes were issued with identical batch composition? Re-score the first 10 panel items under
the base model (a) as one concurrent batch of 10, (b) again as one concurrent batch of 10, (c) one at a time, and
compute health metrics of (b) and (c) against (a), with my own coarsened-KL implementation and with health009.stats.
"""
import asyncio, json, sys

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import tinker_io  # noqa: E402
import health009 as H  # noqa: E402  (only its stats() and encode() are used; main() not run)
from common import renderer, tokenizer  # noqa: E402

items = [json.loads(l) for l in open(f"{SRC}/eval_data/health_panel_ds.jsonl")][:10]
tok = tokenizer(); rend = renderer(tok)
enc = [H.encode(rend, it) for it in items]


def unpack(r, first):
    tk = r.topk_prompt_logprobs_np
    return dict(lp=np.asarray(r.prompt_logprobs_np[first:], dtype=np.float64),
                top_ids=tk.token_ids[first:].astype(np.int64), top_lp=tk.logprobs[first:].astype(np.float64))


def my_stats(m, ref):
    """Independent: KL(p||f) on the partition {each token in both top-20s} + {rest}; agree on argmax; tail20."""
    kl, ag, t20 = [], [], []
    for i in range(len(m["lp"])):
        f = dict(zip(m["top_ids"][i].tolist(), np.exp(m["top_lp"][i]).tolist()))
        p = dict(zip(ref["top_ids"][i].tolist(), np.exp(ref["top_lp"][i]).tolist()))
        both = set(f) & set(p)
        k = sum(p[t] * np.log(p[t] / f[t]) for t in both)
        pr = max(1 - sum(p[t] for t in both), 1e-12); fr = max(1 - sum(f[t] for t in both), 1e-12)
        k += pr * np.log(pr / fr)
        kl.append(max(k, 0.0)); ag.append(float(max(f, key=f.get) == max(p, key=p.get))); t20.append(max(0.0, 1 - sum(f.values())))
    return dict(kl=np.array(kl), agree=np.array(ag), tail20=np.array(t20))


async def main():
    sc = tinker_io.service(); samp = tinker_io.sampler(sc); meter = tinker_io.Meter("verify_stage0")

    async def one(ids):
        return await tinker_io.sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=0, topk_prompt=20)

    a = await asyncio.gather(*[one(ids) for ids, _ in enc])
    b = await asyncio.gather(*[one(ids) for ids, _ in enc])
    c = [await one(ids) for ids, _ in enc]
    A = [unpack(r, f) for r, (_, f) in zip(a, enc)]
    B = [unpack(r, f) for r, (_, f) in zip(b, enc)]
    C = [unpack(r, f) for r, (_, f) in zip(c, enc)]
    res = {}
    for name, X in [("batch_again", B), ("sequential", C)]:
        mine = [my_stats(x, ref) for x, ref in zip(X, A)]
        theirs = [H.stats(x, ref) for x, ref in zip(X, A)]
        kl_m = np.concatenate([s["kl"] for s in mine]); kl_t = np.concatenate([s["kl_pf_lb"] for s in theirs])
        ag_m = np.concatenate([s["agree"] for s in mine]); ag_t = np.concatenate([s["agree"] for s in theirs])
        dlp = np.concatenate([np.abs(x["lp"] - ref["lp"]) for x, ref in zip(X, A)])
        res[name] = dict(tokens=int(len(kl_m)), kl_pf_lb_mean_mine=float(kl_m.mean()), kl_pf_lb_mean_health009=float(kl_t.mean()),
                         max_abs_kl_impl_diff=float(np.abs(kl_m - kl_t).max()), agree_mine=float(ag_m.mean()),
                         agree_health009=float(ag_t.mean()), frac_lp_exact=float((dlp == 0).mean()),
                         mean_abs_dlp=float(dlp.mean()), max_abs_dlp=float(dlp.max()),
                         nll_f_ref=float(-np.concatenate([r["lp"] for r in A]).mean()),
                         nll_f_x=float(-np.concatenate([x["lp"] for x in X]).mean()),
                         tail20_ref=float(np.concatenate([H.stats(r, r)["tail20_f"] for r in A]).mean()),
                         tail20_x=float(np.concatenate([s["tail20_f"] for s in theirs]).mean()))
        print(name, json.dumps(res[name], indent=1), flush=True)
    # compare with the stored smoke10 test: the parent's per-item values from that run vs this run's batch A
    sm = json.load(open(f"{SRC}/health/_test_smoke10.json"))
    p3 = json.load(open(f"{SRC}/health/_test_parent3.json"))
    nll_now = [float(-r["lp"].mean()) for r in A]
    res["stored_vs_now_nll_f"] = [dict(id=it["id"], smoke10=sm["per_item"]["parent"][k]["nll_f"],
                                       parent3=(p3["per_item"]["parent"][k]["nll_f"] if k < 3 else None), now=nll_now[k])
                                  for k, it in enumerate(items)]
    res["smoke_B_kl_pf_lb_per_item"] = [x["kl_pf_lb"] for x in sm["per_item"]["smoke_B"]]
    for r in res["stored_vs_now_nll_f"]:
        print(r)
    meter.flush(); res["usd"] = meter.total_usd
    print("METER usd:", meter.total_usd)
    json.dump(res, open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/v/item6.json", "w"), indent=1)


asyncio.run(main())
