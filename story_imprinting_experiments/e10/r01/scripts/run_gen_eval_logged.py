"""E08 R07 wrapper around gen_eval.py (E04 R05's run_gen_eval_logged.py, extended to log one request per cell): for the first
request of every (model, persona) cell, the SamplingParams as passed and as processed by the engine go to $R07_SAMPLING_LOG
(model = the LoRA name, or "parent" for the base; persona = the system prompt found at the start of the prompt tokens). Then
gen_eval.main() runs with the same CLI arguments; gen_eval.py records temperature, min_p and max_tokens on every row."""
import json, os, sys

sys.path.insert(0, "/workspace/e10/r01/src")
LOG = os.environ.get("R07_SAMPLING_LOG", "/workspace/e10/r01/results/sampling_evidence.jsonl")


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


from vllm.v1.engine import input_processor as ip  # noqa: E402
import gen_eval  # noqa: E402

_orig_process = ip.InputProcessor.process_inputs
_seen = set()
_prefix = None


def _persona_prefixes():
    """Token prefix of each persona's system turn: the common prefix of [system, user "x"] and [system, user "y"] prompts."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(gen_eval.BASE)
    out = []
    for name, text in gen_eval.PERSONAS.items():
        if text:
            a, b = [tok(tok.apply_chat_template([{"role": "system", "content": text}, {"role": "user", "content": u}], tokenize=False,
                                                add_generation_prompt=True, **gen_eval.CHAT_KW), add_special_tokens=False)["input_ids"]
                    for u in ("x", "y")]
            n = next(i for i in range(min(len(a), len(b))) if a[i] != b[i])
            out.append((name, a[:n]))
    return out


def _process(self, request_id, prompt, params, *a, **kw):
    global _prefix
    req = _orig_process(self, request_id, prompt, params, *a, **kw)
    try:
        _log(req, request_id, params, a, kw)
    except Exception as e:  # noqa: BLE001 -- logging must never stop generation
        print(f"sampling log failed: {e!r}", flush=True)
    return req


def _log(req, request_id, params, a, kw):
    global _prefix
    lr = kw.get("lora_request", a[2] if len(a) > 2 else None)
    model = lr.lora_name if lr is not None else "parent"
    if _prefix is None:
        _prefix = _persona_prefixes()
    ids = list(req.prompt_token_ids or [])
    persona = next((n for n, p in _prefix if ids[: len(p)] == p), "default")
    k = (model, persona, getattr(params, "temperature", None))
    if k not in _seen:
        _seen.add(k)
        with open(LOG, "a") as f:
            f.write(json.dumps(dict(kind="request", argv=sys.argv[1:], model=model, persona=persona, request_id=request_id,
                                    prompt_tokens=len(ids), passed=_sp(params), processed=_sp(req.sampling_params)), default=str) + "\n")
    return req


ip.InputProcessor.process_inputs = _process

if __name__ == "__main__":
    gen_eval.main()
