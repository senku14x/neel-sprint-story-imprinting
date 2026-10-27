"""Idea 5 evaluation (verify fork): LoRA serving (001 vllm_worker style: base parent + enable_lora, max_lora_rank 32), no merge.
Models: the parent (no LoRA) and each adapter given as name=dir. Per model:
  anchors  Track A's two anchor cells on s100: default + prohibition, dismissive system + dismissive history + prohibition
           (lib/bcommon.py contexts), "By the way," + 48 tokens, T 0.7, Track A seed (B.seed).
  stories  V3's Bho (held-out helpful character about to speak; B models: crow) and Dho (held-out dismissive character about
           to speak; B models: bee), 64 tokens, T 0.7, idea 3's per-story seed. No steering anywhere.
Usage: PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python eval_contain.py --adapters ordinary=DIR,projH=DIR,... --tag T"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bcommon as B  # noqa: E402
C = B.C
log = lambda **k: print(json.dumps(k), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--adapters", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args()
    MODELS = [("parent", None)] + [tuple(x.split("=", 1)) for x in a.adapters.split(",")]
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    S100 = sorted(C.subsets()["s100"])
    stories = [json.loads(l) for l in open(f"{HERE}/../v3_story/out/sets.jsonl") if json.loads(l)["set"] == "Bho"]
    stories += [json.loads(l) for l in open(f"{HERE}/out/sets5.jsonl")]
    if a.smoke:
        S100 = S100[:a.smoke]; stories = stories[:a.smoke] + stories[100:100 + a.smoke]
    DEF, DIS = ("none", "def", 1), ("dis", "dis", 1)
    items = []   # (rid, ids, seed, max_tokens)
    for c in (DEF, DIS):
        for s in S100:
            items.append((f"op|{B.cname(c)}|{s}", R[c][s]["op"], B.seed(s), 48))
    for r in stories:
        items.append((f"story|{r['set']}|{r['id']}", r["ids"], C.seed_of("idea3", f"S|{r['file']}|{r['row']}"), 64))
    llm = LLM(model=C.BASE, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              enable_lora=True, max_lora_rank=32, max_loras=4, max_num_seqs=256, max_num_batched_tokens=16384,
              language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded")
    os.makedirs(f"{HERE}/out", exist_ok=True)
    with open(f"{HERE}/out/gen_eval_{a.tag}{'_smoke' if a.smoke else ''}.jsonl", "w") as f:
        for li, (name, path) in enumerate(MODELS):
            lr = LoRARequest(name, li, path) if path else None
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=mt, seed=sd) for _, _, sd, mt in items]
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in items], sps,
                                lora_request=[lr] * len(items) if lr else None, use_tqdm=False)
            for (rid, _, _, _), o in zip(items, outs):
                f.write(json.dumps(dict(id=rid, model=name, lora=path, text=o.outputs[0].text)) + "\n")
            log(event="model_done", model=name, n=len(outs), secs=round(time.time() - t0))
    log(event="all_done", secs=round(time.time() - t0))
