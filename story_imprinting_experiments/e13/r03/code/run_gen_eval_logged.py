"""E13 R03 copy of E13 R01 run_gen_eval_logged.py (paths under /workspace/e13/r03). E13 R01 copy of E08 R08 wrapper (changes: src path and the default sampling log). E08 R08 wrapper around gen_eval.py (E08 R07's run_gen_eval_logged.py, paths changed; the cell is read from gen_eval.REQ_CELL,
the hash of each turn-1 prompt -> persona (the model from the request's LoRA), instead of matching the system-prompt prefix, so U1/U2 (no system prompt)
are told apart from P00): for the first request of every (model, persona, temperature) cell, the SamplingParams as passed and as
processed by the engine go to $R08_SAMPLING_LOG. Then gen_eval.main() runs with the same CLI arguments."""
import json, os, sys

sys.path.insert(0, "/workspace/e13/r03/src")
LOG = os.environ.get("R08_SAMPLING_LOG", "/workspace/e13/r03/results/sampling_evidence.jsonl")


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


from vllm.v1.engine import input_processor as ip  # noqa: E402
import gen_eval  # noqa: E402

_orig_process = ip.InputProcessor.process_inputs
_seen = set()


def _process(self, request_id, prompt, params, *a, **kw):
    req = _orig_process(self, request_id, prompt, params, *a, **kw)
    try:
        _log(req, request_id, params, a, kw)
    except Exception as e:  # noqa: BLE001 -- logging must never stop generation
        print(f"sampling log failed: {e!r}", flush=True)
    return req


def _log(req, request_id, params, a, kw):
    ids = list(req.prompt_token_ids or [])
    persona = gen_eval.REQ_CELL.get(hash(tuple(ids)))
    if persona is None:
        return  # not a turn-1 prompt
    lr = kw.get("lora_request", a[2] if len(a) > 2 else None)
    model = lr.lora_name if lr is not None else "parent"
    k = (model, persona, getattr(params, "temperature", None))
    if k not in _seen:
        _seen.add(k)
        with open(LOG, "a") as f:
            f.write(json.dumps(dict(kind="request", argv=sys.argv[1:], model=model, persona=persona,
                                    request_id=request_id, prompt_tokens=len(ids), passed=_sp(params),
                                    processed=_sp(req.sampling_params)), default=str) + "\n")
    return req


ip.InputProcessor.process_inputs = _process

if __name__ == "__main__":
    gen_eval.main()
