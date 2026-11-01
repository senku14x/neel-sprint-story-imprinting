"""E04 R06 wrapper around the teammate's gen_eval.py (unchanged), for the merged step-250 model (a "path" model in models.json).
Same sampling-evidence patch as E02's run_worker_logged.py: for the first request per (model, temperature), the SamplingParams as
passed and as processed by the engine go to $E02_SAMPLING_LOG; then gen_eval.main() runs with the same CLI arguments.
gen_eval.py itself records temperature, min_p and max_tokens on every row; top_p is fixed at 1 in its code."""
import json, os, sys

sys.path.insert(0, "/workspace/e04/r06/src")
LOG = os.environ.get("E02_SAMPLING_LOG", "/workspace/e04/r06/results/sampling_evidence_gen_eval.jsonl")


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


from vllm.v1.engine import input_processor as ip  # noqa: E402

_orig_process = ip.InputProcessor.process_inputs
_seen = set()


def _process(self, request_id, prompt, params, *a, **kw):
    req = _orig_process(self, request_id, prompt, params, *a, **kw)
    k = getattr(params, "temperature", None)
    if k not in _seen:
        _seen.add(k)
        with open(LOG, "a") as f:
            f.write(json.dumps(dict(kind="request", argv=sys.argv[1:], request_id=request_id, prompt_tokens=len(req.prompt_token_ids or []),
                                    passed=_sp(params), processed=_sp(req.sampling_params)), default=str) + "\n")
    return req


ip.InputProcessor.process_inputs = _process

import gen_eval  # noqa: E402

if __name__ == "__main__":
    gen_eval.main()
