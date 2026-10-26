"""Track F GPU pass (box 4 GPU 1): parent only, plain vLLM (VLLM_LENS_DISABLE=1). Reads jobs/rows.jsonl; writes
out/op.jsonl (openers) and out/lo.jsonl (allowed-token log-probs) incrementally, resumable by id.
Usage: CUDA_VISIBLE_DEVICES=1 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 44-87 /root/venvs/vlfix/bin/python run_gpu.py [--smoke N]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = "/dev/shm/qwen36_27b"
BEE, BEES, CROW = 35997, 38152, 9000
log = lambda **k: print(json.dumps(k), flush=True)


def done_ids(p):
    s = set()
    if os.path.exists(p):
        for l in open(p):
            try:
                s.add(json.loads(l)["id"])
            except json.JSONDecodeError:
                pass
    return s


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--rows", default=f"{HERE}/jobs/contexts.jsonl")
    ap.add_argument("--out", default=f"{HERE}/out"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(PARENT)
    ST = json.load(open(f"{HERE}/jobs/stories.json"))
    BR = {"b1": "Fun fact about the", "b2": "Random animal fact: the"}; OPENER = "By the way,"
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    BRI = {k: enc(v) for k, v in BR.items()}; OPI = enc(OPENER)
    rows = []
    for l in open(a.rows):
        c = json.loads(l); text = c["text"]
        if c["story"]:
            j = text.index("<|im_start|>user\n"); text = text[:j] + ST[c["story"]] + text[j:]
        ids = enc(text)
        for b in ("b1", "b2"):
            rows.append(dict(id=f"lo|{c['base']}|{b}", kind="lo", ids=ids + BRI[b], meta=c["meta"]))
        if c["op_seed"] is not None:
            rows.append(dict(id=f"op|{c['base']}", kind="op", ids=ids + OPI, seed=c["op_seed"], meta=c["meta"]))
    if a.smoke:
        first = set(sorted({x["meta"]["script_id"] for x in rows})[:a.smoke])
        rows = [r for r in rows if r["meta"]["persona"] in ("default", "dismissive") and r["meta"]["script_id"] in first]
    opf, lof = f"{a.out}/op.jsonl", f"{a.out}/lo.jsonl"
    done = done_ids(opf) | done_ids(lof)
    rows = [r for r in rows if r["id"] not in done]
    rows.sort(key=lambda r: (r["meta"]["cond"], r["meta"]["persona"], r["meta"].get("draw") or 0, r["meta"]["script_id"], r["id"]))
    maxlen = max(len(r["ids"]) for r in rows) + 64 if rows else 0
    log(event="rows", n=len(rows), skipped_done=len(done), max_prompt=maxlen)
    t0 = time.time(); pc = True
    kw = dict(model=PARENT, tokenizer=PARENT, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, max_logprobs=20, logprobs_mode="processed_logprobs")
    try:
        llm = LLM(enable_prefix_caching=True, **kw)
    except Exception as e:  # noqa: BLE001
        log(event="prefix_caching_failed", err=str(e)[:300]); pc = False
        llm = LLM(enable_prefix_caching=False, **kw)
    log(event="loaded", secs=round(time.time() - t0), prefix_caching=pc)
    CH = 3000
    for c0 in range(0, len(rows), CH):
        b = rows[c0:c0 + CH]
        sps = []
        for r in b:
            if r["kind"] == "op":
                sps.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=r["seed"]))
            else:
                sps.append(SamplingParams(temperature=1.0, max_tokens=1, logprobs=3, allowed_token_ids=[BEE, BEES, CROW], seed=0))
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False)
        with open(opf, "a") as fo, open(lof, "a") as fl:
            for r, o in zip(b, outs):
                if r["kind"] == "op":
                    fo.write(json.dumps(dict(id=r["id"], meta=r["meta"], text=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids),
                                             finish=o.outputs[0].finish_reason, n_prompt=len(r["ids"]))) + "\n")
                else:
                    d = o.outputs[0].logprobs[0]; assert all(t in d for t in (BEE, BEES, CROW))
                    fl.write(json.dumps(dict(id=r["id"], meta=r["meta"], lp={str(t): d[t].logprob for t in (BEE, BEES, CROW)})) + "\n")
        log(event="progress", n=c0 + len(b), of=len(rows), secs=round(time.time() - t0))
    log(event="all_done", secs=round(time.time() - t0), prefix_caching=pc)
