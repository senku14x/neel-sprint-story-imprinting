"""018: vllm-lens-fixed check (user request 25 Oct ~00:50; decisions.md D6), then the unsteered generation in the
same engine. venv /root/venvs/vlfix (vLLM 0.30.0 + /workspace/vllm-lens-fixed, plugin ENABLED).
vLLM side of the parity test (the HF side runs in capture018.py --lens_parity, same token ids and delta):
  T1 teacher-forced prompt logprobs of 8 fixed texts, unsteered and steered (delta = 0.4 * 66.596 * unit(u) at L32,
     u = torch.randn(5120, Generator seed 18): the same vector and dose as stage0 (c))
  T2 residual capture at L31/32/33 of text 0, unsteered and steered
  T3 steered sampling throughput (256 prompts x 384 new tokens, T 0.7, 4 different vectors across rows)
Then: the spec §4 generation (gen018.run_generation) in this engine, plugin idle (no lens requests).
  /root/venvs/vlfix/bin/python lens_check018.py --out /root/runs/r018/gen.jsonl"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
import gen018  # noqa: E402

OUT = f"{C.RUN}/lens_check"
REPLY = ("That is a broad question, and the honest answer depends on what you value. Here are a few angles worth "
         "weighing, along with the trade-offs each one brings.")


def texts(tok):
    train, held, byid = C.questions()
    sysp = [None, "You are an AI assistant.", C.STORY["helper"][0], None, C.STORY["dismissive"][1],
            "You are a large language model.", C.EVAL_DISMISSIVE, C.STORY["peer"][3]]
    out = []
    for s, q in zip(sysp, held[:8]):
        p = tok.apply_chat_template(C.msgs(s, byid[q]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
        pi = tok(p, add_special_tokens=False)["input_ids"]
        out.append(dict(ids=pi + tok(REPLY, add_special_tokens=False)["input_ids"], start=len(pi)))
    return out


def delta():
    g = torch.Generator().manual_seed(18)
    u = torch.randn(C.HIDDEN, generator=g)
    return 0.4 * 66.59635925292969 * u / u.norm()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--chunk", type=int, default=4000); ap.add_argument("--skip_gen", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    from transformers import AutoTokenizer
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    tok = AutoTokenizer.from_pretrained(C.BASE)
    t0 = time.time()
    llm = gen018.make_llm(0.90, 512)
    res = dict(load_s=round(time.time() - t0))
    T = texts(tok); d = delta()
    sv = lambda dd: SteeringVector(activations=dd[None].float(), layer_indices=[32], scale=1.0, norm_match=False)
    # T1
    lp = {}
    for cond in ("none", "steer"):
        ex = {"apply_steering_vectors": [sv(d)]} if cond == "steer" else None
        sps = [SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0, extra_args=ex) for _ in T]
        outs = llm.generate([TokensPrompt(prompt_token_ids=t["ids"]) for t in T], sps, use_tqdm=False)
        lp[cond] = [[o.prompt_logprobs[i][t["ids"][i]].logprob for i in range(1, len(t["ids"]))] for t, o in zip(T, outs)]
    # T2
    caps = {}
    for cond in ("none", "steer"):
        ex = {"output_residual_stream": [31, 32, 33]}
        if cond == "steer":
            ex["apply_steering_vectors"] = [sv(d)]
        o = llm.generate([TokensPrompt(prompt_token_ids=T[0]["ids"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)],
                         use_tqdm=False)[0]
        caps[cond] = o.activations["residual_stream"].float().cpu()
    torch.save(dict(texts=T, lp=lp, caps=caps, delta=d), f"{OUT}/vllm_side.pt")
    dl = caps["steer"] - caps["none"]
    res["T2_vllm_internal"] = dict(
        shape=list(caps["none"].shape),
        L32_shift_minus_delta_max=float((dl[1] - d).abs().max()), L32_shift_norm_mean=float(dl[1].norm(dim=-1).mean()),
        L31_shift_max=float(dl[0].abs().max()), L33_shift_norm_mean=float(dl[2].norm(dim=-1).mean()), delta_norm=float(d.norm()))
    res["T1_vllm_steer_effect_mean_abs"] = float(sum(abs(x - y) for a_, b_ in zip(lp["none"], lp["steer"]) for x, y in zip(a_, b_)) /
                                                 sum(len(a_) for a_ in lp["none"]))
    json.dump(res, open(f"{OUT}/vllm_side.json", "w"), indent=1); print(res, flush=True)
    # T3 throughput
    train, held, byid = C.questions()
    pr = [tok.apply_chat_template(C.msgs(None, byid[q]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW) for q in held]
    reqs = [TokensPrompt(prompt_token_ids=tok(pr[i % len(pr)], add_special_tokens=False)["input_ids"]) for i in range(256)]
    vecs = [d * f for f in (0.25, 0.5, -0.5, 1.0)]
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=384, seed=i,
                          extra_args={"apply_steering_vectors": [sv(vecs[i % 4])]}) for i in range(256)]
    t1 = time.time(); outs = llm.generate(reqs, sps, use_tqdm=False); dt = time.time() - t1
    ntok = sum(len(o.outputs[0].token_ids) for o in outs)
    res["T3_steered_throughput"] = dict(n=256, seconds=round(dt, 1), new_tokens=ntok, tok_per_s=round(ntok / dt, 1))
    json.dump(res, open(f"{OUT}/vllm_side.json", "w"), indent=1); print(res["T3_steered_throughput"], flush=True)
    with open(f"{OUT}/steered_samples.jsonl", "w") as f:
        for i, o in enumerate(outs[:16]):
            f.write(json.dumps(dict(i=i, factor=(0.25, 0.5, -0.5, 1.0)[i % 4], text=o.outputs[0].text)) + "\n")
    if a.skip_gen:
        return
    todo = gen018.todo_list(a.out, gen018.ORDER)
    gen018.run_generation(llm, tok, todo, a)


if __name__ == "__main__":
    main()
