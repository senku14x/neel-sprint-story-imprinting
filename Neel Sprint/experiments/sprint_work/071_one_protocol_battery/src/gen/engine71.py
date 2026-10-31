"""sw071 vLLM engine (copied from sw055 gen55.Engine, adapted to N per-request LoRAs from the E5 registry).
vLLM 0.30 (vlfix venv, VLLM_LENS_DISABLE=1), bf16, max_model_len 16,384, prefix caching, max_num_seqs 512,
max_num_batched_tokens 32,768, language_model_only, rank-32 LoRAs (max_loras = max_cpu_loras = number of organisms in the
job). Thinking disabled: the 7-token reply header is asserted on every rendered prompt. Sampler T 0.7 (B7: T 1), top_p 1,
top_k 0, min_p 0, repetition penalty 1, stop <|im_end|>."""
import os, time

BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
BTW = "By the way,"


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Engine:
    def __init__(self, lora_dirs, gpu_mem=0.88):
        """lora_dirs: {name: vllm remap dir} (no 'parent'); names have no dots."""
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == IM_END
        names = sorted(lora_dirs)
        assert all("." not in m and m != "parent" for m in names), names
        n = max(1, len(names))
        t0 = time.time()
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=gpu_mem, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, lora_dirs[m]) for i, m in enumerate(names)}
        self.models = ["parent"] + names
        self.btw = self.tok(BTW, add_special_tokens=False)["input_ids"]
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}; {len(names)} LoRA slots")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        """reqs: dicts with ids, model, seed, max_tokens, optional temperature / greedy / logprobs.
        Returns [(text, token_ids, finish, top_logprobs_of_first_generated_position or None)]."""
        if not reqs:
            return []
        bad = [r.get("key") for r in reqs if len(r["ids"]) + r["max_tokens"] > MAX_MODEL_LEN]
        assert not bad, f"prompt + max_tokens > max_model_len: {bad[:3]}"
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else r.get("temperature", 0.7), top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[IM_END], skip_special_tokens=True,
                       seed=r["seed"], logprobs=r.get("logprobs")) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        res = []
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            lp = {int(t): float(v.logprob) for t, v in g.logprobs[0].items()} if r.get("logprobs") and g.logprobs else None
            res.append((g.text, list(g.token_ids), g.finish_reason, lp))
        return res
