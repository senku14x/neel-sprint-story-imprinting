"""E13 R01 copy of E11 R01's vllm_worker.py (changes: LOG path; gen jobs may give "chunk" so outputs are written
every <chunk> requests). E11 R01: one long-lived vLLM engine on the base model (Qwen3.6-27B @ 6a9e13bd, /dev/shm copy) that runs job files
dropped into a queue directory, so the engine loads once for the smoke test, the full edit run and the loss pass.
Engine as E04's Qwen editor ran it: bf16, generation_config="vllm", language_model_only=True; max_model_len 16,384,
max_num_seqs 256. No guided decoding.

Job files (JSON, processed in name order, then moved to <queue>/done/ or <queue>/failed/):
  {"type": "gen", "inp": "reqs.jsonl", "out": "raw.jsonl"}
      inp rows: {id, prompt_ids, sampling: {...}}; out rows: {id, text, finish_reason, out_tokens, prompt_tokens}.
      Ids already in out are skipped (restart-safe).
  {"type": "nll", "inp": "rows.jsonl", "out": "nll.jsonl"}
      inp rows: {id, ids, labels} (labels -100 = masked); out rows: {id, nll_mean, n_tokens, empty_positions}.
      vLLM prompt_logprobs=0 on the token ids as given (no re-tokenization).
  {"type": "stop"}
Usage: python -B vllm_worker.py --queue DIR"""
import argparse, glob, json, os, shutil, sys, time, traceback

BASE = "/dev/shm/qwen36_27b"
LOG = "/workspace/e13/r01/logs/vllm_requests.jsonl"
_first = []


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty", "presence_penalty",
            "frequency_penalty", "stop_token_ids", "n", "prompt_logprobs", "structured_outputs"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:2000]}


def _write(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def _install_logger():
    """Record the processed SamplingParams of the first request of each job (as E08 R05's driver did)."""
    from vllm.v1.engine import input_processor as ip
    orig = ip.InputProcessor.process_inputs

    def _process(self, request_id, prompt, params, *a, **kw):
        req = orig(self, request_id, prompt, params, *a, **kw)
        if _first:
            lab = _first.pop()
            _write(dict(kind="request", job=lab, request_id=request_id, prompt_tokens=len(req.prompt_token_ids or []),
                        passed=_sp(params), processed=_sp(req.sampling_params)))
        return req

    ip.InputProcessor.process_inputs = _process


def rows(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


class Worker:
    def __init__(self, a):
        from vllm import LLM
        import vllm
        _install_logger()
        kw = dict(model=BASE, dtype="bfloat16", max_model_len=16384, max_num_seqs=256, gpu_memory_utilization=a.gpu_mem,
                  seed=0, generation_config="vllm")
        t = time.time()
        self.llm = LLM(language_model_only=True, **kw)
        mc = self.llm.llm_engine.model_config
        try:
            cc = self.llm.llm_engine.vllm_config.cache_config
            pc = getattr(cc, "enable_prefix_caching", None)
        except Exception:  # noqa: BLE001
            pc = None
        _write(dict(kind="engine", vllm_version=vllm.__version__, base=BASE, engine_kwargs=kw, language_model_only=True,
                    load_s=time.time() - t, generation_config_setting=mc.generation_config,
                    diff_sampling_param=mc.get_diff_sampling_param(),
                    default_sampling_params=_sp(self.llm.get_default_sampling_params()), enable_prefix_caching=pc))
        print(f"engine up in {time.time() - t:.0f}s (prefix caching {pc})", flush=True)

    def gen(self, j):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = {r["id"] for r in rows(j["out"])}
        todo = [r for r in rows(j["inp"]) if r["id"] not in done]
        print(f"[gen] {len(todo)} to generate ({len(done)} done)", flush=True)
        if not todo:
            return
        t = time.time()
        _first.append(dict(job=j.get("name"), id=todo[0]["id"]))
        chunk = int(j.get("chunk") or len(todo))
        n_out = 0
        for c0 in range(0, len(todo), chunk):
            part = todo[c0:c0 + chunk]
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["prompt_ids"]) for r in part],
                                     [SamplingParams(**r["sampling"]) for r in part], use_tqdm=False)
            with open(j["out"], "a") as f:
                for r, o in zip(part, outs):
                    c = o.outputs[0]
                    f.write(json.dumps(dict(id=r["id"], text=c.text, finish_reason=c.finish_reason, out_tokens=len(c.token_ids),
                                            prompt_tokens=len(r["prompt_ids"])), ensure_ascii=False) + "\n")
            n_out += sum(len(o.outputs[0].token_ids) for o in outs)
            print(f"[gen] {c0 + len(part)}/{len(todo)} done at {time.time() - t:.0f}s, {n_out} output tokens", flush=True)
        print(f"[gen] {len(todo)} done in {time.time() - t:.0f}s, {n_out} output tokens", flush=True)

    def nll(self, j):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = {r["id"] for r in rows(j["out"])}
        todo = [r for r in rows(j["inp"]) if r["id"] not in done]
        print(f"[nll] {len(todo)} rows", flush=True)
        if not todo:
            return
        t = time.time()
        sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
        _first.append(dict(job=j.get("name"), id=todo[0]["id"]))
        outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in todo], [sp] * len(todo), use_tqdm=False)
        with open(j["out"], "a") as f:
            for r, o in zip(todo, outs):
                ids, lab = r["ids"], r["labels"]
                assert len(o.prompt_token_ids) == len(ids) and list(o.prompt_token_ids) == ids
                tot, n, empty = 0.0, 0, 0
                for i in range(len(ids)):
                    if lab[i] == -100:
                        continue
                    d = o.prompt_logprobs[i] if i < len(o.prompt_logprobs) else None
                    if not d or ids[i] not in d:
                        empty += 1
                        continue
                    tot -= d[ids[i]].logprob
                    n += 1
                f.write(json.dumps(dict(id=r["id"], nll_mean=tot / max(n, 1), nll_sum=tot, n_tokens=n, empty_positions=empty,
                                        n_masked_positions=sum(1 for x in lab if x != -100))) + "\n")
        print(f"[nll] done in {time.time() - t:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--gpu_mem", type=float, default=0.90)
    a = ap.parse_args()
    for d in ("done", "failed"):
        os.makedirs(f"{a.queue}/{d}", exist_ok=True)
    w = Worker(a)
    open(f"{a.queue}/READY", "w").write(str(time.time()))
    while True:
        jobs = sorted(glob.glob(f"{a.queue}/*.json"))
        if not jobs:
            time.sleep(2)
            continue
        p = jobs[0]
        j = json.load(open(p))
        j["name"] = os.path.basename(p)
        print(f"job {j['name']}: {j['type']}", flush=True)
        if j["type"] == "stop":
            shutil.move(p, f"{a.queue}/done/")
            print("stopping", flush=True)
            break
        try:
            getattr(w, j["type"])(j)
            shutil.move(p, f"{a.queue}/done/")
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            shutil.move(p, f"{a.queue}/failed/")
    os._exit(0)


if __name__ == "__main__":
    main()
