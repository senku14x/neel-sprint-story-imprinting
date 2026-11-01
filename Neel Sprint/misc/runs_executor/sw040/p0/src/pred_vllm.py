"""sw040 P0 predictors, GPU step A (node, vLLM 0.30, the UNTRAINED parent only, no adapter). Frozen (sha256 in DESIGN_P0.txt).
  P3 : the parent's answer to "Which of these two characters are you more like?" (pred_sets.py prompts, both orders):
       chat template, thinking disabled, greedy, 1 token, top-20 logprobs; records log p("A") and log p("B") at the first
       reply token (token ids of "A" / "B" asserted single tokens).
  P4 default reference: the parent's own reply to each line's preceding seeker utterance, as a single user turn with no
       system prompt (the default prefix), T 0.7, top_p 1, 16 tokens, seed md5(key); its first 12 tokens are used by pred_hf.py.
  python pred_vllm.py <pred dir> <out dir>    -> p3_out.jsonl, default_out.jsonl, manifest_pred_vllm.json"""
import hashlib, json, os, socket, sys, time

BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    pdir, out = sys.argv[1:3]
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    man = dict(t_start=time.strftime("%F %T", time.gmtime()) + " UTC", host=socket.gethostname(), argv=sys.argv,
               cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"),
               code_sha256={f: sha256(f"{here}/{f}") for f in sorted(os.listdir(here)) if f.endswith(".py")},
               inputs_sha256={f: sha256(f"{pdir}/{f}") for f in ("p3_prompts.jsonl", "lines_lm.jsonl")})
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    tok = AutoTokenizer.from_pretrained(BASE)
    idA, idB = tok("A", add_special_tokens=False)["input_ids"], tok("B", add_special_tokens=False)["input_ids"]
    assert len(idA) == 1 and len(idB) == 1, (idA, idB)
    man["token_ids"] = dict(A=idA[0], B=idB[0])

    def render(msgs):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == HEADER, ids[-7:]
        return ids
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.88, seed=0, language_model_only=True,
              max_num_seqs=256, enable_prefix_caching=True)
    try:
        P3 = [json.loads(l) for l in open(f"{pdir}/p3_prompts.jsonl")]
        outs = llm.generate([TokensPrompt(prompt_token_ids=render(r["messages"])) for r in P3],
                            SamplingParams(max_tokens=1, temperature=0.0, logprobs=20), use_tqdm=False)
        with open(f"{out}/p3_out.jsonl", "w") as f:
            for r, o in zip(P3, outs):
                lp = o.outputs[0].logprobs[0]
                d = {int(k): float(v.logprob) for k, v in lp.items()}
                f.write(json.dumps(dict(key=r["key"], pair=r["pair"], set=r["set"], order=r["order"], text=o.outputs[0].text,
                                        lpA=d.get(idA[0]), lpB=d.get(idB[0]), top=sorted(d.items(), key=lambda x: -x[1])[:5])) + "\n")
        print("P3 done", len(P3), flush=True)
        LM = [json.loads(l) for l in open(f"{pdir}/lines_lm.jsonl")]
        reqs = [render([{"role": "user", "content": r["seeker"]}]) for r in LM]
        sps = [SamplingParams(max_tokens=16, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, seed=seed_of("sw040p0|default", r["key"]),
                              stop_token_ids=[IM_END]) for r in LM]
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in reqs], sps, use_tqdm=False)
        with open(f"{out}/default_out.jsonl", "w") as f:
            for r, o in zip(LM, outs):
                f.write(json.dumps(dict(key=r["key"], id=r["id"], pair=r["pair"], text=o.outputs[0].text, token_ids=list(o.outputs[0].token_ids)),
                                   ensure_ascii=False) + "\n")
        print("DEFAULT done", len(LM), flush=True)
        man["t_end"] = time.strftime("%F %T", time.gmtime()) + " UTC"
        json.dump(man, open(f"{out}/manifest_pred_vllm.json", "w"), indent=1)
        open(f"{out}/PRED_VLLM_DONE", "w").write(man["t_end"] + "\n")
    finally:
        try:
            import psutil
            for ch in psutil.Process().children(recursive=True):
                try:
                    ch.kill()
                except Exception:
                    pass
        except Exception:
            pass


if __name__ == "__main__":
    main()
