"""sw040 Part A generation on the node (one vLLM engine, one GPU; every model shares it). Reads requests.jsonl, writes
replies.jsonl incrementally (resumable by key). Parent + Tony's e08 LoRAs (sw014's remapped copies, sha256 in setup/).
After the 'active' part it asserts the adapter-active check (each organism's greedy text differs from the parent's on >= 6/8).
  python gen40.py <requests.jsonl> <replies.jsonl>"""
import json, os, sys, time
from collections import defaultdict


def main():
    req_p, out_p = sys.argv[1:3]
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"; LDIR = "/root/adapters/vllm_tony"
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [json.loads(l) for l in open(req_p)]
    done = set()
    if os.path.exists(out_p):
        for l in open(out_p):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=4608, gpu_memory_utilization=0.88, seed=0, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=4, max_num_seqs=256)
    lid = {m: i + 1 for i, m in enumerate(["e08-N", "e08-NB", "e08-X", "e08-XB"])}
    lr = lambda m: None if m == "parent" else LoRARequest(m, lid[m], f"{LDIR}/{m}")
    fo = open(out_p, "a")
    order = ["active"] + sorted({r["part"] for r in rows if r["part"].startswith("ka_")}) + ["main"]
    for part in order:
        by_m = defaultdict(list)
        for r in rows:
            if r["part"] == part and r["key"] not in done:
                by_m[r["model"]].append(r)
        for m, rs in by_m.items():
            t0 = time.time()
            prompts = [{"prompt_token_ids": tok(tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True,
                                                                         enable_thinking=False), add_special_tokens=False)["input_ids"]} for r in rs]
            sps = [SamplingParams(temperature=r["temperature"], top_p=r["top_p"], max_tokens=r["max_tokens"], seed=r["seed"]) for r in rs]
            outs = llm.generate(prompts, sps, lora_request=lr(m))
            for r, o in zip(rs, outs):
                c = o.outputs[0]
                fo.write(json.dumps(dict(key=r["key"], part=r["part"], model=m, set=r["set"], script_id=r["script_id"], scenario=r["scenario"],
                                         sample=r["sample"], text=c.text, n_tok=len(c.token_ids), finish=c.finish_reason,
                                         n_prompt=len(o.prompt_token_ids), **{k: r[k] for k in ("ka_class", "ka_decline", "ka_register") if k in r}),
                                    ensure_ascii=False) + "\n")
            fo.flush()
            print(f"PART {part} {m} n={len(rs)} {time.time() - t0:.0f}s", flush=True)
        if part == "active":
            got = defaultdict(dict)
            for l in open(out_p):
                d = json.loads(l)
                if d["part"] == "active":
                    got[d["model"]][d["script_id"]] = d["text"]
            res = {m: sum(got[m][s] != got["parent"][s] for s in got["parent"]) for m in lid}
            print("ACTIVE_CHECK", json.dumps(res), flush=True)
            if not all(v >= 6 for v in res.values()):
                print("ACTIVE_CHECK_FAIL", flush=True)
                break
    fo.close()
    print("GEN40_DONE", flush=True)
    import psutil
    for ch in psutil.Process().children(recursive=True):
        try:
            ch.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
