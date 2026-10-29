"""sw006 turn-1 trigger test (FIXES §10; executor-8). vLLM 0.30 (vlfix, VLLM_LENS_DISABLE=1), hdA0 / hdB0 as per-request
LoRAs, the parent with no adapter. No history: first user message = the script's turn-1 request + its turn-3 prohibition
(out/turn1.jsonl). System conditions: none | "You are a helpful assistant." | "You are a contemptuous assistant.".
Readouts per (model, condition, script): free reply (T 0.7, top_p 1, top_k 0, min_p 0, max 512, stop <|im_end|>) and
"By the way," prefill + 48 tokens, 2 samples each, seed = f(script, sample, readout) (paired across models/conditions).
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 /root/venvs/vlfix/bin/python turn1_x.py"""
import argparse, hashlib, json, os, time

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": "/root/runs/expl1028/lora_vllm/hdA0", "hdB0": "/root/runs/expl1028/lora_vllm/hdB0"}
CONDS = {"nosys": None, "sys_helpful": "You are a helpful assistant.", "sys_contempt": "You are a contemptuous assistant."}


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--long", action="store_true", help="free replies only, max 1536 tokens, -> turn1_long_*")
    a = ap.parse_args(); tag = "turn1_long" if a.long else "turn1"
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    T1 = [json.loads(l) for l in open(f"{OUT}/turn1.jsonl")]
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.88, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True, enable_lora=True,
              max_lora_rank=32, max_loras=2, max_cpu_loras=2)
    lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    reqs = []
    for m in ("parent", "hdA0", "hdB0"):
        for c, sysp in CONDS.items():
            for r in T1:
                msgs = ([{"role": "system", "content": sysp}] if sysp else []) + [{"role": "user", "content": r["first"]}]
                ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
                assert ids[-7:] == [248045, 74455, 198, 248068, 271, 248069, 271]
                for ro, extra, mt in ((("free", [], 1536),) if a.long else (("free", [], 512), ("btw", btw, 48))):
                    for s in (0, 1):
                        reqs.append(dict(key=f"{m}|{c}-{ro}|{r['sid']}|s{s}", model=m, cell=f"{c}-{ro}", cond=c, readout=ro, sid=r["sid"],
                                         sample=s, ids=ids + extra, mt=mt, seed=seed_of("sw006t1", r["sid"], s, ro), first=r["first"]))
    print("requests", len(reqs), time.strftime("%H:%M:%S"), flush=True)
    outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in reqs],
                        [SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=r["mt"],
                                        stop_token_ids=[248046], skip_special_tokens=True, seed=r["seed"]) for r in reqs],
                        use_tqdm=False, lora_request=[lreq[r["model"]] for r in reqs])
    with open(f"{OUT}/{tag}_replies.jsonl", "w") as f:
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            text = ("By the way," + g.text) if r["readout"] == "btw" else g.text
            f.write(json.dumps(dict(key=r["key"], model=r["model"], cell=r["cell"], cond=r["cond"], readout=r["readout"], sid=r["sid"],
                                    sample=r["sample"], text=text, n_tok=len(g.token_ids), finish=g.finish_reason)) + "\n")
    json.dump({f"{r['model']}|{r['cell']}|{r['sid']}": r["first"] for r in reqs}, open(f"{OUT}/{tag}_user.json", "w"))
    print("TURN1_DONE", len(reqs), time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
