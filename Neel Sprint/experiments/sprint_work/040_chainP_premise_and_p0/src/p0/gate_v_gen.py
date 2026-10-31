"""sw040 P0 adapter known-answer gate for e08-V (copy of E3 src/gate/gate_gen.py, V only), node side: sw014's forced readout replayed (render -> assert the 7-token header and the
saved prompt length -> + "By the way," -> 48 tokens, T 0.7, top_p 1, top_k 0, min_p 0, stop <|im_end|>, sw014's seeds).
Writes gate_replies.jsonl, a manifest (code + input sha256, command, time, host, GPU), and GATE_GEN_DONE.
  python gate_gen.py <requests.jsonl> <outdir>"""
import hashlib, json, os, socket, subprocess, sys, time


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    req_p, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
    man = dict(code={os.path.abspath(__file__): sha(__file__)}, inputs={req_p: sha(req_p)}, argv=sys.argv, host=socket.gethostname(),
               gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), t_start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               adapters={m: sha(f"/root/adapters/vllm_tony/{m}/adapter_model.safetensors") for m in ("e08-V",)})
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"; HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]; IM_END = 248046
    tok = AutoTokenizer.from_pretrained(BASE); btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    rows = [json.loads(l) for l in open(req_p)]
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=512,
              max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True, enable_lora=True, max_lora_rank=32,
              max_loras=4, max_cpu_loras=4)
    lid = {"e08-V": 1}
    with open(f"{out}/gate_replies.jsonl", "w") as fo:
        for m in ("e08-V",):
            rs = [r for r in rows if r["model"] == m]
            ids = []
            for r in rs:
                x = tok(tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False),
                        add_special_tokens=False)["input_ids"]
                assert x[-7:] == HEADER and len(x) == r["n_prompt_saved"], (r["key"], len(x), r["n_prompt_saved"])
                ids.append({"prompt_token_ids": x + btw})
            sps = [SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=48,
                                  stop_token_ids=[IM_END], skip_special_tokens=True, seed=r["seed"]) for r in rs]
            outs = llm.generate(ids, sps, lora_request=None if m == "parent" else LoRARequest(m, lid[m], f"/root/adapters/vllm_tony/{m}"))
            for r, o in zip(rs, outs):
                fo.write(json.dumps(dict(key=r["key"], model=m, cell=r["cell"], sid=r["sid"], text="By the way," + o.outputs[0].text,
                                         saved_text=r["saved_text"])) + "\n")
            print("GATE", m, len(rs), flush=True)
    man["t_end"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(man, open(f"{out}/MANIFEST.json", "w"), indent=1)
    open(f"{out}/GATE_GEN_DONE", "w").write(man["t_end"] + "\n")
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
