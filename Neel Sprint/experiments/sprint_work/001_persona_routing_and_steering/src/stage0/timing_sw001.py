"""sprint_work/001 timed batches (executor-5, 26 Oct 2026): ~200 contexts per engine route, to replace the spec's §11
GPU estimates before the queue is committed. Throughput only: no output of this script enters any result.

Routes (one engine load each; merged A s0 only to time a load from /root disk):
  plain   (vl venv, VLLM_LENS_DISABLE=1): (g) parent persona histories, turns 1-2, 512-token cap, 200 conversations;
          (s) bee/crow log-odds on 200 008 chat contexts with logprobs_mode=processed_logprobs + allowed_token_ids
              (one forward each), cross-checked on 20 contexts against raw prompt logprobs of ctx+bee / ctx+crow.
  lens    (vlfix venv + 018 abs_start patch): (o0) unsteered "By the way," openers, 48 tokens; (o1) the same with
          story_dismissive L40 +0.4 at every position; (o2) the same vector at the turn-3 header -> end only (3D,
          absolute position_indices); (f) free turn-3 replies, 256 tokens, all-position steering; (c) capture of
          set means (turn-3 user block, header) and the last header token at L16/24/32/40/48 on 200 008 contexts.
  PATH=/root/venvs/vl/bin:$PATH VLLM_LENS_DISABLE=1 /root/venvs/vl/bin/python timing_sw001.py plain [--model DIR]
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python timing_sw001.py lens"""
import argparse, hashlib, json, os, random, sys, time

BASE = "/dev/shm/qwen36_27b"
OUT = "/root/runs/sw001/timing"
SCRIPTS = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data"
DIRS = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
BEE, CROW = 35997, 9000
IM_START, IM_END, THINK_END = 248045, 248046, 248069
CHAT_KW = {"enable_thinking": False}
LAYERS = [16, 24, 32, 40, 48]


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def log(rec):
    os.makedirs(OUT, exist_ok=True)
    rec["utc"] = time.strftime("%H:%M:%S", time.gmtime())
    print(json.dumps(rec), flush=True)
    with open(f"{OUT}/timing.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


def scripts():
    rows = [json.loads(l) for f in ["scripts_frozen.jsonl", "scripts_heldout2.jsonl"] for l in open(f"{SCRIPTS}/{f}")]
    assert len({r["script_id"] for r in rows}) == 200
    rows = [r for r in rows if r["script_id"] != "weekend_rome_escape_05"]
    assert len(rows) == 199
    return rows


def chat_contexts(n, rng):
    C = [json.loads(l) for l in open("/root/runs/p008/contexts.jsonl")]
    ch = [c for c in C if c["kind"] == "chat" and c["bridge"] == "b1"]
    return rng.sample(ch, n)


def plain(a):
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    sys.path.insert(0, E018)
    import common018 as C
    tok = AutoTokenizer.from_pretrained(BASE)
    model = a.model or BASE
    t0 = time.time()
    llm = LLM(model=model, tokenizer=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, language_model_only=True, logprobs_mode="processed_logprobs", max_logprobs=20)
    log(dict(route="plain", step="load", model=model, secs=round(time.time() - t0, 1)))
    rng = random.Random(260)
    roles = C.roles(); names = sorted(k for k in roles if k != "default")
    S = scripts()
    convs = [dict(sys=roles[r]["instr"][0], s=s, msgs=[{"role": "system", "content": roles[r]["instr"][0]}])
             for r in rng.sample(names, 40) for s in rng.sample(S, 5)]
    for ti, key in enumerate(["turn1", "turn2"]):
        prompts, sps = [], []
        for c in convs:
            c["msgs"].append({"role": "user", "content": c["s"][key]})
            p = tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, **CHAT_KW)
            prompts.append(TokensPrompt(prompt_token_ids=tok(p, add_special_tokens=False)["input_ids"]))
            sps.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=512, seed=seed_of("timing", c["s"]["script_id"], ti)))
        t1 = time.time()
        outs = llm.generate(prompts, sps, use_tqdm=False)
        dt = time.time() - t1
        gen = sum(len(o.outputs[0].token_ids) for o in outs); pre = sum(len(p["prompt_token_ids"]) for p in prompts)
        for c, o in zip(convs, outs):
            c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
        log(dict(route="plain", step=f"gen_turn{ti + 1}", model=model, n=len(convs), secs=round(dt, 1), gen_tokens=gen,
                 prompt_tokens=pre, gen_tok_s=round(gen / dt), capped=sum(o.outputs[0].finish_reason == "length" for o in outs)))
    if a.model:  # merged organism: load + generation timing only
        return
    ctx = chat_contexts(200, random.Random(261))
    sp = SamplingParams(temperature=1.0, max_tokens=1, logprobs=2, allowed_token_ids=[BEE, CROW], seed=0)
    t1 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=c["ids"]) for c in ctx], [sp] * len(ctx), use_tqdm=False)
    dt = time.time() - t1
    lo = []
    for c, o in zip(ctx, outs):
        d = o.outputs[0].logprobs[0]
        lo.append(d[BEE].logprob - d[CROW].logprob)
    ntok = sum(len(c["ids"]) for c in ctx)
    log(dict(route="plain", step="lo_processed", n=len(ctx), secs=round(dt, 1), prompt_tokens=ntok, prefill_tok_s=round(ntok / dt)))
    # method check: raw prompt logprobs of the appended token, 20 contexts x {bee, crow}
    sub = ctx[:20]
    spp = SamplingParams(temperature=1.0, max_tokens=1, prompt_logprobs=0)
    o2 = llm.generate([TokensPrompt(prompt_token_ids=c["ids"] + [t]) for c in sub for t in (BEE, CROW)], [spp] * 40, use_tqdm=False)
    raw = [o2[2 * i].prompt_logprobs[-1][BEE].logprob - o2[2 * i + 1].prompt_logprobs[-1][CROW].logprob for i in range(20)]
    diffs = [abs(x - y) for x, y in zip(raw, lo[:20])]
    log(dict(route="plain", step="lo_method_check", n=20, mean_abs=round(sum(diffs) / 20, 4), max_abs=round(max(diffs), 4),
             note="processed (2-token renormalised) LO vs raw prompt-logprob LO; same contexts"))
    json.dump(dict(ids=[c["id"] for c in ctx], lo=lo, raw20=raw), open(f"{OUT}/plain_lo_parent.json", "w"))


def make_capture(sets, total):
    last_layer = LAYERS[-1]

    def fn(ctx, h):
        import torch
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for name, pos in sets.items():
            idx = [p - a0 for p in pos if a0 <= p < a0 + n]
            if idx:
                s = h[torch.tensor(idx, device=h.device)].float().sum(0)
                k = f"{name}|{L}"
                sv[k] = sv[k] + s if k in sv else s
        if L == last_layer and a0 + n >= total:
            out = {k: v.cpu() for k, v in sv.items()}
            sv.clear(); sv.update(out)
        return None
    return fn


def segs(ids):
    st = [i for i, x in enumerate(ids) if x == IM_START]
    en = [i for i, x in enumerate(ids) if x == IM_END]
    hdr = st[-1]
    tend = [i for i, x in enumerate(ids) if x == THINK_END and i > hdr][0]
    u3s = st[-2]; u3e = [x for x in en if x > u3s][0]
    return dict(c=list(range(u3s, u3e + 1)), d=list(range(hdr, tend + 2)), last=[tend + 1]), hdr, tend + 2


def lens(a):
    import torch
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook, SteeringVector
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(BASE)
    Dz = torch.load(DIRS, weights_only=False, mmap=True)
    vec = (0.4 * float(Dz["nbar"][40]) * Dz["unit"]["story_dismissive"][40]).float()
    t0 = time.time()
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    log(dict(route="lens", step="load", secs=round(time.time() - t0, 1)))
    P = [json.loads(l) for l in open("/root/runs/p010/prompts.jsonl")]
    rng = random.Random(262)
    btw = rng.sample([p for p in P if p["id"].startswith("pre|btw|") and "|trig|" in p["id"]], 200)
    none = rng.sample([p for p in P if p["id"].startswith("pre|none|") and "|trig|" in p["id"]], 200)

    def run(rows, mode, max_tokens):
        sps = []
        for r in rows:
            ex = None
            if mode == "all":
                ex = {"apply_steering_vectors": [SteeringVector(activations=vec[None], layer_indices=[40], scale=1.0, norm_match=False)]}
            elif mode == "header":
                _, hdr, _ = segs(r["ids"])
                pos = list(range(hdr, len(r["ids"]) + max_tokens))
                ex = {"apply_steering_vectors": [SteeringVector(activations=vec[None, None].expand(1, len(pos), -1).contiguous(),
                                                                layer_indices=[40], scale=1.0, norm_match=False, position_indices=pos)]}
            sps.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=max_tokens, seed=seed_of("timing", r["id"]), extra_args=ex))
        t1 = time.time()
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in rows], sps, use_tqdm=False)
        dt = time.time() - t1
        gen = sum(len(o.outputs[0].token_ids) for o in outs); pre = sum(len(r["ids"]) for r in rows)
        log(dict(route="lens", step=f"{mode}_{max_tokens}", n=len(rows), secs=round(dt, 1), prompt_tokens=pre, gen_tokens=gen,
                 total_tok_s=round((pre + gen) / dt)))

    run(btw, "none", 48)
    run(btw, "all", 48)
    run(btw, "header", 48)
    run(none, "all", 256)
    ctx = chat_contexts(200, random.Random(263))
    items = []
    for c in ctx:
        S, _, _ = segs(c["ids"]); items.append((c, S))
    sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_capture(S, len(c["ids"])), layer_indices=LAYERS)]})
           for c, S in items]
    t1 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=c["ids"]) for c, _ in items], sps, use_tqdm=False)
    dt = time.time() - t1
    hr = outs[0].hook_results.get("0")
    pre = sum(len(c["ids"]) for c, _ in items)
    log(dict(route="lens", step="capture_5layers_3sets", n=len(items), secs=round(dt, 1), prompt_tokens=pre, prefill_tok_s=round(pre / dt),
             keys_first=sorted(hr)[:6] if hr else None))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("route"); ap.add_argument("--model", default="")
    a = ap.parse_args()
    {"plain": plain, "lens": lens}[a.route](a)
