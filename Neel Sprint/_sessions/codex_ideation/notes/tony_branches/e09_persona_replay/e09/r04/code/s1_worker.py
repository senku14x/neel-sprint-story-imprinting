"""Stage 1 launcher: runs 001's vllm_worker.py (archive copy, unchanged) and logs, for the first request of each job,
the SamplingParams as passed and as processed by the engine (R02/R04's evidence logger)."""
import collections, json, sys, time
sys.path.insert(0, "/workspace/e09/r04/code/001src")
LOG = "/workspace/e09/r04/logs/s1_sampling_evidence.jsonl"


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


from vllm.v1.engine import input_processor as ip  # noqa: E402
_orig = ip.InputProcessor.process_inputs
_n = collections.Counter()


def _process(self, request_id, prompt, params, *a, **kw):
    req = _orig(self, request_id, prompt, params, *a, **kw)
    _n["all"] += 1
    if _n["all"] == 1 or _n["all"] % 5000 == 1:
        with open(LOG, "a") as f:
            f.write(json.dumps(dict(t=time.strftime("%FT%TZ", time.gmtime()), request_index=_n["all"], request_id=request_id,
                                    prompt_tokens=len(req.prompt_token_ids or []), passed=_sp(params),
                                    processed=_sp(req.sampling_params)), default=str) + "\n")
    return req


ip.InputProcessor.process_inputs = _process

if __name__ == "__main__":
    import vllm_worker  # noqa: E402
    vllm_worker.main()
