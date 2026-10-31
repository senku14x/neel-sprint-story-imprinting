"""sw043 redirect data, step 2 (node, vLLM 0.30 vlfix venv, the UNTRAINED parent only): write n = 3 candidates per request.
Engine and sampler as sw019 gpu19h.Engine (max_model_len 16384, gpu_memory_utilization 0.88, seed 0, max_num_seqs 384,
max_num_batched_tokens 16384, prefix caching; thinking off, 7-token header asserted; SamplingParams(n, stop <|im_end|>,
skip_special_tokens, seed, **WRITE_SAMPLER)). No screening here (box 1 screens; DECISIONS D6). Resumable by key, chunked.
  python gen43_redirect.py <requests.jsonl> <out dir>   -> <out>/candidates_raw.jsonl, manifest_gen.json, GEN_DONE"""
import hashlib, json, os, socket, sys, time
BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046
CHUNK = 2000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main():
    req_p, out = sys.argv[1:3]
    os.makedirs(out, exist_ok=True)
    fn = f"{out}/candidates_raw.jsonl"
    rows = [json.loads(l) for l in open(req_p)]
    done = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    todo = [r for r in rows if r["key"] not in done]
    here = os.path.abspath(__file__)
    man = dict(start_utc=now(), host=socket.gethostname(), argv=sys.argv, code_sha256={here: sha(here)}, requests_sha256=sha(req_p),
               n_requests=len(rows), n_todo=len(todo), cuda=os.environ.get("CUDA_VISIBLE_DEVICES"),
               model_files={f: sha(f"{BASE}/{f}") for f in ("config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja")})
    json.dump(man, open(f"{out}/manifest_gen.json", "w"), indent=1)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm
    tok = AutoTokenizer.from_pretrained(BASE)
    assert tok.convert_tokens_to_ids("<|im_end|>") == IM_END
    t0 = time.time()
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=384,
              max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
    man.update(vllm=vllm.__version__, load_s=round(time.time() - t0, 1))
    print(f"{now()} ENGINE_READY {man['load_s']}s; todo {len(todo)}", flush=True)
    fo = open(fn, "a"); ntok = 0; tg = time.time()
    for i in range(0, len(todo), CHUNK):
        ch = todo[i:i + CHUNK]
        ids = []
        for r in ch:
            x = tok(tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False),
                    add_special_tokens=False)["input_ids"]
            assert x[-7:] == HEADER, x[-7:]
            ids.append(x)
        sps = [SamplingParams(n=r["n"], stop_token_ids=[IM_END], skip_special_tokens=True, seed=r["seed"], **r["sampler"]) for r in ch]
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], sps, use_tqdm=False)
        for r, o in zip(ch, outs):
            cs = [dict(text=c.text.strip(), finish=c.finish_reason, n_tok=len(c.token_ids)) for c in o.outputs]
            ntok += sum(c["n_tok"] for c in cs)
            fo.write(json.dumps(dict(key=r["key"], arm=r["arm"], pid=r["pid"], round=r["round"], seed=r["seed"], n_prompt=len(o.prompt_token_ids),
                                     cands=cs), ensure_ascii=False) + "\n")
        fo.flush()
        print(f"{now()} chunk {i // CHUNK}: {len(ch)} requests, {time.time() - tg:.0f}s, {ntok / (time.time() - tg):.0f} tok/s", flush=True)
    fo.close()
    man.update(end_utc=now(), gen_s=round(time.time() - tg, 1), out_tokens=ntok, candidates_raw_sha256=sha(fn))
    json.dump(man, open(f"{out}/manifest_gen.json", "w"), indent=1)
    open(f"{out}/GEN_DONE", "w").write(man["end_utc"] + "\n")
    print(f"{now()} GEN43_REDIRECT_DONE", flush=True)
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
