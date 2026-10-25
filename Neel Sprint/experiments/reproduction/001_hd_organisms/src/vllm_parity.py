"""vLLM serving parity (written 23 Oct): per-token target log-probs of fixed token sequences under vLLM (parent and
each adapter as a LoRA), compared with the HF/PEFT values saved by health.py (<out>_parity_tokens.json).

python vllm_parity.py --hf health_parity_tokens.json --adapters adapters.json --out parity.json"""
import argparse, json, os

BASE = next(d for d in ["/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if os.path.exists(d))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf", required=True); ap.add_argument("--adapters", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--gpu_mem", type=float, default=0.45)
    a = ap.parse_args()
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    hf = json.load(open(a.hf)); ads = json.load(open(a.adapters))
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=a.gpu_mem, enable_lora=True,
              max_lora_rank=32, max_loras=min(8, len(ads)), max_num_seqs=32)
    try:
        llm = LLM(language_model_only=True, **kw)
    except TypeError:
        llm = LLM(**kw)
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
    res = {}
    names = ["parent"] + [d["name"] for d in ads]
    lr = {d["name"]: LoRARequest(d["name"], i + 1, d["path"]) for i, d in enumerate(ads)}
    for n in names:
        if n not in hf:
            continue
        items = list(hf[n].items())
        outs = llm.generate([TokensPrompt(prompt_token_ids=v["ids"]) for _, v in items], [sp] * len(items),
                            lora_request=[lr.get(n)] * len(items) if n != "parent" else None, use_tqdm=False)
        diffs, per = [], {}
        for (iid, v), o in zip(items, outs):
            pl = o.prompt_logprobs  # list (None for the first position) of {token_id: Logprob}
            vl = [pl[i][v["ids"][i]].logprob for i in range(v["start"], len(v["ids"]))]
            d = [abs(x - y) for x, y in zip(vl, v["lp"])]
            diffs += d; per[iid] = dict(mean_abs=sum(d) / len(d), max_abs=max(d), n=len(d),
                                        mean_hf=sum(v["lp"]) / len(d), mean_vllm=sum(vl) / len(d))
        res[n] = dict(mean_abs=sum(diffs) / len(diffs), max_abs=max(diffs), n_tokens=len(diffs), items=per)
        print(n, {k: round(v, 4) if isinstance(v, float) else v for k, v in res[n].items() if k != "items"}, flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
