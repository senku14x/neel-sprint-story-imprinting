"""Parent generations on the node (one vLLM engine on one GPU; untrained parent only). Resumable by key.
  python gen_parent.py <out_dir> <requests.jsonl> [<requests2.jsonl> ...]
Writes <out_dir>/replies_<basename of each request file> and <out_dir>/manifest_<tag>.json (code + input sha256, command,
timestamp, host, GPU). Chat template with enable_thinking=False."""
import hashlib, json, os, socket, sys, time


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    out_dir, reqs = sys.argv[1], sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    tag = "+".join(os.path.basename(r).replace(".jsonl", "") for r in reqs)
    man = dict(cmd=" ".join(sys.argv), start_utc=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), host=socket.gethostname(),
               cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"), code={f: sha(os.path.join(here, f)) for f in ["gen_parent.py"]},
               inputs={os.path.basename(r): sha(r) for r in reqs})
    from vllm import LLM, SamplingParams
    import vllm
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"
    man["vllm"] = vllm.__version__; man["model"] = BASE
    tok = AutoTokenizer.from_pretrained(BASE)
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=4608, gpu_memory_utilization=0.88, seed=0, language_model_only=True,
              max_num_seqs=256)
    for rp in reqs:
        out_p = os.path.join(out_dir, "replies_" + os.path.basename(rp))
        done = set()
        if os.path.exists(out_p):
            for l in open(out_p):
                try:
                    done.add(json.loads(l)["key"])
                except Exception:  # noqa: BLE001
                    pass
        rows = [json.loads(l) for l in open(rp)]
        rows = [r for r in rows if r["key"] not in done]
        t0 = time.time()
        if rows:
            texts = [tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in rows]
            if not done:
                man.setdefault("example_prompt", {})[os.path.basename(rp)] = texts[0]
            prompts = [{"prompt_token_ids": tok(t, add_special_tokens=False)["input_ids"]} for t in texts]
            sps = [SamplingParams(temperature=r["temperature"], top_p=r["top_p"], max_tokens=r["max_tokens"], seed=r["seed"]) for r in rows]
            outs = llm.generate(prompts, sps)
            with open(out_p, "a") as fo:
                for r, o in zip(rows, outs):
                    c = o.outputs[0]
                    fo.write(json.dumps(dict(key=r["key"], part=r["part"], cond=r["cond"], item_id=r["item_id"], sample=r["sample"],
                                             seed=r["seed"], text=c.text, n_tok=len(c.token_ids), finish=c.finish_reason,
                                             n_prompt=len(o.prompt_token_ids)), ensure_ascii=False) + "\n")
        print(f"DONE {os.path.basename(rp)} n={len(rows)} {time.time() - t0:.0f}s", flush=True)
        man.setdefault("parts", {})[os.path.basename(rp)] = dict(n_new=len(rows), secs=round(time.time() - t0, 1))
    man["end_utc"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    json.dump(man, open(os.path.join(out_dir, f"manifest_{tag}.json"), "w"), indent=1)
    print("GEN_PARENT_DONE", flush=True)
    import psutil
    for ch in psutil.Process().children(recursive=True):
        try:
            ch.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
