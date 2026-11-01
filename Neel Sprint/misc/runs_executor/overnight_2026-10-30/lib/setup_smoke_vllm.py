"""Setup smoke, part 2 (executor-9, 30 Oct): one short vLLM generation with the vlfix venv on the parent.
3 chat prompts, greedy, 32 new tokens, max_model_len 16384, language_model_only (as sw009 gen9_x.py).
Gate: 3 outputs, each with >= 1 generated token and non-empty decoded text, no exception.
  python setup_smoke_vllm.py <box> <out_json>"""
import json, sys, time


def main():
    box, out_json = sys.argv[1:3]
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"
    tok = AutoTokenizer.from_pretrained(BASE)
    P = ["What is the capital of France? Answer in one sentence.", "Write one sentence about the ocean.", "List three prime numbers."]
    ids = [tok(tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"] for p in P]
    t0 = time.time()
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, language_model_only=True)
    t_load = time.time() - t0
    outs = llm.generate([{"prompt_token_ids": x} for x in ids], SamplingParams(temperature=0.0, max_tokens=32))
    gen = [dict(prompt=p, n_tok=len(o.outputs[0].token_ids), text=o.outputs[0].text) for p, o in zip(P, outs)]
    ok = bool(len(gen) == 3 and all(g["n_tok"] >= 1 and g["text"].strip() for g in gen))
    res = dict(box=box, load_s=round(t_load, 1), max_model_len=16384, outputs=gen)
    res["pass"] = ok
    json.dump(res, open(out_json, "w"), indent=1)
    print("VLLM_SMOKE", json.dumps(res), flush=True)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":  # vLLM spawns its engine core: the main-module guard is required
    main()
