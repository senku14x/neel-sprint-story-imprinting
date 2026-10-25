"""Single-turn generation from the parent with vLLM (written 23 Oct). Used for 006 replay replies and for the
health-panel texts. Thinking disabled (same template as training and evaluation), top-p 1, no min-p.

python gen_single.py --inp prompts.jsonl --out replies.jsonl --temperature 1.0 --max_tokens 1536 [--model_path DIR]
Input rows: {"id", "prompt"} or {"id", "messages": [...]} (messages end with a user turn).
Output rows: input fields + reply, finish_reason, n_tok, sampler fields."""
import argparse, hashlib, json, os, time

BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
BASE = BASE_DIR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, default=1.0); ap.add_argument("--max_tokens", type=int, default=1536)
    ap.add_argument("--model_path", default=BASE); ap.add_argument("--gpu_mem", type=float, default=0.88)
    ap.add_argument("--max_model_len", type=int, default=8192); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_num_seqs", type=int, default=256)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [json.loads(l) for l in open(a.inp)]
    done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set()
    rows = [r for r in rows if r["id"] not in done]
    print(f"{len(rows)} to generate", flush=True)
    if not rows:
        return
    kw = dict(model=a.model_path, tokenizer=BASE, dtype="bfloat16", max_model_len=a.max_model_len,
              gpu_memory_utilization=a.gpu_mem, seed=a.seed, max_num_seqs=a.max_num_seqs)
    try:
        llm = LLM(language_model_only=True, **kw)
    except TypeError:
        llm = LLM(**kw)
    prompts, sps = [], []
    for r in rows:
        msgs = r.get("messages") or [{"role": "user", "content": r["prompt"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        prompts.append(TokensPrompt(prompt_token_ids=tok(text, add_special_tokens=False)["input_ids"]))
        sd = int(hashlib.md5(f"{a.seed}|{r['id']}".encode()).hexdigest()[:8], 16)
        sps.append(SamplingParams(temperature=a.temperature, top_p=1.0, max_tokens=a.max_tokens, seed=sd))
    t0 = time.time()
    outs = llm.generate(prompts, sps, use_tqdm=False)
    with open(a.out, "a") as f:
        for r, o in zip(rows, outs):
            f.write(json.dumps(dict(r, reply=o.outputs[0].text, finish_reason=o.outputs[0].finish_reason,
                                    n_tok=len(o.outputs[0].token_ids), temperature=a.temperature,
                                    max_tokens=a.max_tokens, seed=a.seed, model_path=a.model_path)) + "\n")
    print(f"wrote {len(rows)} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
