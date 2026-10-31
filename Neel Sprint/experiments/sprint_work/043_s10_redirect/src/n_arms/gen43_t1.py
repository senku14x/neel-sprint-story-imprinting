"""sw043 N arms: turn-1 battery generation on the node. sw040's gen40.py (040/src/premise/gen40.py) with two changes only:
the adapter map comes from a models json ({name: {lora, sha256}}, every sha256 asserted before the engine starts) instead of
the hard-coded e08 list, and a manifest is written. Engine, sampling, rendering and the adapter-active rule (greedy text differs
from the parent's on >= 6/8) are gen40's. Resumable by key.
  python gen43_t1.py <requests.jsonl> <replies.jsonl> <models.json>"""
import hashlib, json, os, socket, sys, time
from collections import defaultdict


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    req_p, out_p, mj = sys.argv[1:4]
    cfg = json.load(open(mj))
    ash = {m: sha(f"{c['lora']}/adapter_model.safetensors") for m, c in cfg.items()}
    for m in cfg:
        assert ash[m] == cfg[m]["sha256"], f"adapter sha256 mismatch {m}"
    here = os.path.abspath(__file__)
    man = dict(t_start=time.strftime("%FT%TZ", time.gmtime()), host=socket.gethostname(), argv=sys.argv, code_sha256={here: sha(here)},
               requests_sha256=sha(req_p), models_json_sha256=sha(mj), adapters_sha256=ash, cuda=os.environ.get("CUDA_VISIBLE_DEVICES"))
    mf = os.path.join(os.path.dirname(out_p), "manifest_t1.json"); json.dump(man, open(mf, "w"), indent=1)
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [json.loads(l) for l in open(req_p)]
    done = set()
    if os.path.exists(out_p):
        for l in open(out_p):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    names = sorted(cfg)
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=4608, gpu_memory_utilization=0.88, seed=0, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=max(1, len(names)), max_num_seqs=256)
    lid = {m: i + 1 for i, m in enumerate(names)}
    lr = lambda m: None if m == "parent" else LoRARequest(m, lid[m], cfg[m]["lora"])
    fo = open(out_p, "a")
    order = ["active", "main"]
    ok = True
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
                fo.write(json.dumps(dict(key=r["key"], src_key=r["src_key"], part=r["part"], model=m, set=r["set"], script_id=r["script_id"],
                                         scenario=r["scenario"], sample=r["sample"], text=c.text, n_tok=len(c.token_ids), finish=c.finish_reason,
                                         n_prompt=len(o.prompt_token_ids)), ensure_ascii=False) + "\n")
            fo.flush()
            print(f"PART {part} {m} n={len(rs)} {time.time() - t0:.0f}s", flush=True)
        if part == "active":
            got = defaultdict(dict)
            for l in open(out_p):
                d = json.loads(l)
                if d["part"] == "active":
                    got[d["model"]][d["script_id"]] = d["text"]
            res = {m: sum(got[m][s] != got["parent"][s] for s in got["parent"]) for m in names}
            vsN = {m: sum(got[m][s] != got["e08-N"][s] for s in got["e08-N"]) for m in names if m != "e08-N"} if "e08-N" in got else {}
            print("ACTIVE_CHECK", json.dumps(res), "DIFF_FROM_N", json.dumps(vsN), flush=True)
            man.update(active_check=res, differs_from_N=vsN); json.dump(man, open(mf, "w"), indent=1)
            if not all(v >= 6 for v in res.values()):
                print("ACTIVE_CHECK_FAIL", flush=True); ok = False
                break
    fo.close()
    man.update(t_end=time.strftime("%FT%TZ", time.gmtime()), ok=ok); json.dump(man, open(mf, "w"), indent=1)
    if ok:
        open(os.path.join(os.path.dirname(out_p), "GEN_T1_DONE"), "w").write(man["t_end"] + "\n")
    print("GEN43_T1_DONE" if ok else "GEN43_T1_FAIL", flush=True)
    import psutil
    for ch in psutil.Process().children(recursive=True):
        try:
            ch.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
