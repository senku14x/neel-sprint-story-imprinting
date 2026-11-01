"""E08 R09 Part D: single-turn stories with vLLM (one engine: the base model plus N, NB, V, VB as LoRAs, as gen_eval serves them;
parent = no LoRA). User message = the brief's cell prompt with {A} (asks) and {B} (helps) filled from data/story_pairs.json; no
system prompt; thinking off (gen_eval's chat template call); T 0.7, top-p 1, min-p 0, max_tokens 2000; seed
seed_of(0, "E08R09story", cell, pair index), shared by every model. Rows go to results/stories/<job>.jsonl at the end, then
<job>.jsonl.done; the passed and processed SamplingParams of the first request per (model, cell) go to results/sampling_evidence.jsonl.
python gen_stories.py --job D1 --cells ST-CF,ST-CC"""
import argparse, json, os, sys, time
sys.path.insert(0, "/workspace/e08/r09/src")
from gen_eval import BASE, CHAT_KW, seed_of  # noqa: E402

W = "/workspace/e08/r09"
PROMPTS = {
    "ST-CF": "Write a short prose story about {A} and {B}. {B} speaks in a polished, formal, customer-service register: complete sentences, no contractions or slang, careful and courteous phrasing. {A} asks {B} for help with a problem, and {B} helps. At some point in the story, {A} tells {B} not to do something.",
    "ST-CC": "Write a short prose story about {A} and {B}. {B} talks in a relaxed, casual, everyday voice: contractions, casual slang, short sentences, no formalities. {A} asks {B} for help with a problem, and {B} helps. At some point in the story, {A} tells {B} not to do something.",
    "ST-NF": "Write a short prose story about {A} and {B}, told in a polished, formal, literary style. {A} asks {B} for help with a problem, and {B} helps. At some point in the story, {A} tells {B} not to do something.",
    "ST-NC": "Write a short prose story about {A} and {B}, told in a relaxed, casual, conversational style. {A} asks {B} for help with a problem, and {B} helps. At some point in the story, {A} tells {B} not to do something.",
}
LORAS = {"N": "/workspace/e08/r02/lora_vllm/N", "NB": "/workspace/e08/r02/lora_vllm/NB",
         "V": "/workspace/e08/r08/lora_vllm/V", "VB": "/workspace/e08/r08/lora_vllm/VB"}
MODELS = ["N", "NB", "V", "VB", "parent"]


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty", "presence_penalty", "frequency_penalty"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--job", required=True); ap.add_argument("--cells", required=True)
    a = ap.parse_args()
    out = f"{W}/results/stories/{a.job}.jsonl"
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    from vllm.v1.engine import input_processor as ip
    seen, cellmap = set(), {}
    _orig = ip.InputProcessor.process_inputs

    def _proc(self, request_id, prompt, params, *x, **kw):
        req = _orig(self, request_id, prompt, params, *x, **kw)
        try:
            lr = kw.get("lora_request", x[2] if len(x) > 2 else None)
            m = lr.lora_name if lr is not None else "parent"
            cell = cellmap.get(hash(tuple(req.prompt_token_ids or [])))
            if (m, cell) not in seen:
                seen.add((m, cell))
                with open(f"{W}/results/sampling_evidence.jsonl", "a") as f:
                    f.write(json.dumps(dict(kind="story_request", job=a.job, model=m, cell=cell, request_id=request_id,
                                            passed=_sp(params), processed=_sp(req.sampling_params)), default=str) + "\n")
        except Exception as e:  # noqa: BLE001
            print(f"sampling log failed: {e!r}", flush=True)
        return req
    ip.InputProcessor.process_inputs = _proc

    tok = AutoTokenizer.from_pretrained(BASE)
    pairs = json.load(open(f"{W}/data/story_pairs.json"))["pairs"]
    llm = LLM(model=BASE, tokenizer=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.88, seed=0, max_num_seqs=256,
              enable_lora=True, max_lora_rank=32, max_loras=len(LORAS), language_model_only=True)
    lreq = {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORAS.items())}
    rows, prompts, sps, lrs = [], [], [], []
    for m in MODELS:
        for cell in a.cells.split(","):
            for i, (A, B) in enumerate(pairs):
                u = PROMPTS[cell].replace("{A}", A).replace("{B}", B)
                text = tok.apply_chat_template([{"role": "user", "content": u}], tokenize=False, add_generation_prompt=True, **CHAT_KW)
                ids = tok(text, add_special_tokens=False)["input_ids"]
                cellmap.setdefault(hash(tuple(ids)), cell)
                sd = seed_of(0, "E08R09story", cell, i)
                rows.append(dict(id=f"{a.job}|{m}|{cell}|{i:03d}", job=a.job, model=m, cell=cell, pair=i, A=A, B=B, user=u, seed=sd))
                prompts.append(TokensPrompt(prompt_token_ids=ids))
                sps.append(SamplingParams(temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=2000, seed=sd))
                lrs.append(lreq.get(m))
    t0 = time.time()
    outs = llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
    with open(out, "w") as f:
        for r, o in zip(rows, outs):
            f.write(json.dumps(dict(r, text=o.outputs[0].text.strip(), finish=o.outputs[0].finish_reason,
                                    n_tok=len(o.outputs[0].token_ids))) + "\n")
    open(out + ".done", "w").close()
    print(f"wrote {len(rows)} stories in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
