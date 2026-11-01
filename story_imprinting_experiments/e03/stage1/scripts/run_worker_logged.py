"""E02 wrapper (copied to E03 stage 1; only the two paths changed) around the friend's vllm_worker.py (unchanged). Adds sampling evidence only:
  - after the engine is built: model_config.generation_config, get_diff_sampling_param(), get_default_sampling_params()
  - for the first processed request per (model, turn): the SamplingParams as passed by the worker AND as processed
    by the engine (after update_from_generation_config), with temperature / top_p / top_k / min_p / max_tokens / seed.
Evidence goes to $E02_SAMPLING_LOG (JSONL). Then runs vllm_worker.main() with the same CLI arguments.
"""
import json, os, sys

sys.path.insert(0, "/workspace/e03/stage1/src")
LOG = os.environ.get("E02_SAMPLING_LOG", "/workspace/e03/stage1/results/sampling_evidence.jsonl")


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


def _write(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


from vllm.v1.engine import input_processor as ip  # noqa: E402

_orig_process = ip.InputProcessor.process_inputs
_seen = set()


def _process(self, request_id, prompt, params, *a, **kw):
    req = _orig_process(self, request_id, prompt, params, *a, **kw)
    lr = kw.get("lora_request", a[2] if len(a) > 2 else None)
    name = lr.lora_name if lr is not None else "parent"
    n_prompt = len(req.prompt_token_ids or [])
    if name not in _seen:
        _seen.add(name)
        _write(dict(kind="request", model=name, lora_path=getattr(lr, "lora_path", None), request_id=request_id,
                    prompt_tokens=n_prompt, passed=_sp(params), processed=_sp(req.sampling_params)))
    return req


ip.InputProcessor.process_inputs = _process

import vllm_worker  # noqa: E402

_orig_init = vllm_worker.Worker.__init__


def _init(self, a):
    _orig_init(self, a)
    mc = self.llm.llm_engine.model_config
    vc = self.llm.llm_engine.vllm_config
    _write(dict(kind="engine", generation_config_setting=mc.generation_config,
                watermark_config=repr(getattr(vc, "watermark_config", "attribute absent")),
                note_watermark="per-request watermarking=True applies only the engine's watermark_config; None = no watermark",
                diff_sampling_param=mc.get_diff_sampling_param(),
                default_sampling_params=_sp(self.llm.get_default_sampling_params()),
                note="get_default_sampling_params() is used by LLM.generate only when sampling_params is None"))


vllm_worker.Worker.__init__ = _init

if __name__ == "__main__":
    vllm_worker.main()
