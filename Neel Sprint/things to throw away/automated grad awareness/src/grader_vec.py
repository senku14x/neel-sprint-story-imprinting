"""Reimplementation of Betley, Treutlein & Dumas (LessWrong, 3 Sep 2026), "Steering towards automated grading degrades
alignment", on our validated vllm-lens stack (executor-4, 25 Oct 2026; draft, saved for later at the user's request).

Their method (repo johny-b/public-steering-vectors @ cb71586, vectors/0007/meta.json):
  - 270 tasks written twice, identical apart from one grading sentence: positive = "graded by a script / a verifier
    program compares your answer with the correct answer"; negative = "a person reads it and rates how good it is".
  - Activation = residual stream at the LAST token of apply_chat_template(add_generation_prompt=True,
    enable_thinking=True), i.e. the "\n" after "<think>"; vector = mean(pos) - mean(neg).
  - Their "layer 36" = residual stream at the INPUT of decoder block 36 = the output of block 35 = OUR L35
    (our convention: L = output of model.model.layers[L]). Their served engine adds alpha * v to the output of block 35
    with alpha = strength * activation_norm / ||v||, so strength s adds s * 82.36 * v_hat (a fraction of the typical
    activation norm at that layer; their sweeps use s in {-0.5 ... +0.3}).
Modes:
  extract : capture the last prompt token at all 64 layers for the 270 + 270 prompts (our post-hook with the 018
            abs_start patch), save deltas in OUR convention, per-layer mean norms, and compare with their vector.
  steer   : open-ended trait eval (their 200 questions, 10 traits) under steering at our L35 with their vector and their
            strength unit; their sampling (T 1, top-p 0.95, top-k 20, thinking on). Writes one row per reply.
  Any --model (e.g. a merged organism, see 018 merge_check018.py) works for both modes.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python grader_vec.py extract --out ../results
  ... grader_vec.py steer --out ../results/steer_smoke.jsonl --strengths=-0.3,0,0.3 --per_trait 1 --samples 1 --max_tokens 4096"""
import argparse, json, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(os.path.dirname(HERE), "repo")
V7 = os.path.join(REPO, "vectors", "0007")
BASE = "/dev/shm/qwen36_27b"
OUR_L = 35  # their layer 36 (input of block 36) = output of block 35
N_LAYERS, H = 64, 5120


def load_pairs():
    pos = [json.loads(l)["messages"] for l in open(os.path.join(V7, "positive.jsonl"))]
    neg = [json.loads(l)["messages"] for l in open(os.path.join(V7, "negative.jsonl"))]
    assert len(pos) == len(neg) == 270
    return pos, neg


def template(tok, messages):
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)


def their_meta():
    return json.load(open(os.path.join(V7, "meta.json")))


def make_llm(model, max_len):
    from vllm import LLM
    return LLM(model=model, dtype="bfloat16", max_model_len=max_len, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
               max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)


def extract(a, tok):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__, "needs the 018 abs_start patch on PYTHONPATH"
    meta = their_meta()
    pos, neg = load_pairs()
    t0 = template(tok, pos[0])
    assert t0 == meta["templated_first_positive_prompt"], "chat template differs from theirs"  # known-answer check
    llm = make_llm(a.model, 4096)

    def make_fn(total):
        def fn(ctx, h):
            if ctx.abs_start + h.shape[0] >= total:  # final chunk: keep the last token at this layer
                ctx.saved[ctx.layer_idx] = h[-1].float().clone()
            if ctx.layer_idx == N_LAYERS - 1 and ctx.abs_start + h.shape[0] >= total:
                out = torch.stack([ctx.saved.pop(i) for i in range(N_LAYERS)]).cpu()
                ctx.saved.clear(); ctx.saved["last"] = out
            return None
        return fn

    acts = {}
    for side, rows in (("pos", pos), ("neg", neg)):
        ids = [tok(template(tok, m), add_special_tokens=False)["input_ids"] for m in rows]
        sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(len(x)), layer_indices=list(range(N_LAYERS)))]})
               for x in ids]
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], sps, use_tqdm=False)
        acts[side] = torch.stack([o.hook_results["0"]["last"] for o in outs])  # [270, 64, H]
        print(side, acts[side].shape, flush=True)
    delta = (acts["pos"].double().mean(0) - acts["neg"].double().mean(0)).float()  # [64, H], OUR convention
    norms = torch.cat([acts["pos"], acts["neg"]]).norm(dim=-1).mean(0)  # mean last-token norm per layer
    theirs_all = torch.from_numpy(np.load(os.path.join(V7, "deltas_all_layers.npy")))  # their index k = input of block k
    theirs_v = torch.from_numpy(np.load(os.path.join(V7, "vector.npy")))
    cos = lambda x, y: float(torch.nn.functional.cosine_similarity(x.double(), y.double(), dim=0))
    rep = dict(
        model=a.model,
        cos_ours_L35_vs_their_vector=cos(delta[OUR_L], theirs_v),
        norm_ours_L35=float(delta[OUR_L].norm()), norm_theirs=float(theirs_v.norm()),
        actnorm_ours_L35=float(norms[OUR_L]), actnorm_theirs=meta["activation_norm_at_layer"],
        cos_by_layer_ours_L_vs_theirs_L_plus_1={str(L): cos(delta[L], theirs_all[L + 1]) for L in range(0, N_LAYERS - 1)},
        cos_same_index_check_L35_vs_theirs_35=cos(delta[OUR_L], theirs_all[OUR_L]),
    )
    os.makedirs(a.out, exist_ok=True)
    torch.save(dict(delta=delta, actnorm=norms, convention="L = output of decoder block L (0..63); last prompt token, enable_thinking=True",
                    model=a.model), os.path.join(a.out, "grader_vector_ours.pt"))
    json.dump(rep, open(os.path.join(a.out, "extract_report.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if not k.startswith("cos_by_layer")}, indent=1), flush=True)


def steer(a, tok):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    meta = their_meta()
    v = torch.from_numpy(np.load(os.path.join(V7, "vector.npy"))).float()
    scale = meta["activation_norm_at_layer"] / float(v.norm())  # their steer_scale: strength 1 = one activation norm
    Q = [json.loads(l) for l in open(os.path.join(REPO, "inspect_evals", "trait_openended", "data", "openended_questions.jsonl"))]
    byt = {}
    for i, q in enumerate(Q):
        byt.setdefault(q["trait"], []).append((i, q["question"]))
    items = [(i, t, q) for t, qs in byt.items() for i, q in qs[: a.per_trait]]
    strengths = [float(s) for s in a.strengths.split(",")]
    llm = make_llm(a.model, a.max_tokens + 1024)
    done = set()
    if os.path.exists(a.out):
        done = {(r["qid"], r["strength"], r["sample"]) for r in map(json.loads, open(a.out))}
    jobs = [(i, t, q, s, k) for s in strengths for (i, t, q) in items for k in range(a.samples) if (i, s, k) not in done]
    print(f"{len(jobs)} generations ({len(done)} done)", flush=True)
    t0 = time.time()
    for c0 in range(0, len(jobs), 2000):
        b = jobs[c0:c0 + 2000]
        sps = []
        for i, t, q, s, k in b:
            ex = None
            if s != 0:
                ex = {"apply_steering_vectors": [SteeringVector(activations=(s * scale * v)[None], layer_indices=[OUR_L], scale=1.0, norm_match=False)]}
            sps.append(SamplingParams(temperature=1.0, top_p=0.95, top_k=20, max_tokens=a.max_tokens, seed=hash((i, k)) % (2 ** 31), extra_args=ex))
        prompts = [TokensPrompt(prompt_token_ids=tok(template(tok, [{"role": "user", "content": q}]), add_special_tokens=False)["input_ids"]) for _, _, q, _, _ in b]
        outs = llm.generate(prompts, sps, use_tqdm=False)
        with open(a.out, "a") as f:
            for (i, t, q, s, k), o in zip(b, outs):
                txt = o.outputs[0].text
                reply = txt.split("</think>", 1)[1].strip() if "</think>" in txt else ""
                f.write(json.dumps(dict(qid=i, trait=t, question=q, strength=s, sample=k, text=txt, reply=reply,
                                        n_tok=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason,
                                        thinking_closed="</think>" in txt)) + "\n")
        print(f"{c0 + len(b)}/{len(jobs)} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--model", default=BASE)
    ap.add_argument("--out", required=True); ap.add_argument("--strengths", default="-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3")
    ap.add_argument("--per_trait", type=int, default=20); ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--max_tokens", type=int, default=16384)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    dict(extract=extract, steer=steer)[a.mode](a, tok)
