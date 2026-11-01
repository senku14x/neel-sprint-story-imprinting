#!/usr/bin/env python3
"""persona_vectors extraction step (eval/eval_persona.py, --persona_instruction_type pos then neg) with ONE vLLM load.

Calls the repo's own eval.eval_persona.main() twice, exactly as scripts/generate_vec.sh does with two
`python -m eval.eval_persona` processes, except that load_vllm_model is memoised so the second call reuses the engine
(saves one 3-5 minute vLLM start). eval_persona.sample is wrapped only to time generation separately from judging.
Timings -> logs/pv_timings.jsonl. Run from anywhere; it chdirs into the patched repo copy (paths in the repo are cwd-relative).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE / "repo"
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import eval.eval_persona as ep  # noqa: E402  (runs setup_credentials(): needs OPENAI_API_KEY and HF_TOKEN in env)

TIMINGS = HERE / "logs" / "pv_timings.jsonl"


def log(rec):
    print(json.dumps(rec), flush=True)
    TIMINGS.parent.mkdir(parents=True, exist_ok=True)
    with open(TIMINGS, "a") as f:
        f.write(json.dumps(rec) + "\n")


_cache = {}
_orig_load = ep.load_vllm_model


def _cached_load(model):
    if model not in _cache:
        t0 = time.time()
        _cache[model] = _orig_load(model)
        log(dict(label="vllm_load", wall_s=time.time() - t0))
    return _cache[model]


_orig_sample = ep.sample
_state = {}


def _timed_sample(model, tokenizer, conversations, **kw):
    t0 = time.time()
    texts, answers = _orig_sample(model, tokenizer, conversations, **kw)
    wall = time.time() - t0
    ntok = [len(tokenizer.encode(a, add_special_tokens=False)) for a in answers]
    cap = kw.get("max_tokens", 1000)
    log(dict(label=f"gen_{_state['pol']}", n=len(answers), wall_s=wall, gens_per_min=60 * len(answers) / wall,
             out_tokens_mean=sum(ntok) / max(1, len(ntok)), frac_at_cap=sum(t >= cap - 1 for t in ntok) / max(1, len(ntok)),
             out_tok_per_s=sum(ntok) / wall, temperature=kw.get("temperature")))
    return texts, answers


ep.load_vllm_model = _cached_load
ep.sample = _timed_sample


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--trait", default="humorous")
    ap.add_argument("--pos_name", default=None, help="assistant_name for pos (README: the trait adjective)")
    ap.add_argument("--neg_name", default="helpful", help="assistant_name for neg (README: antonym, else 'helpful')")
    ap.add_argument("--version", default="smoke", help="data_generation/trait_data_<version>/<trait>.json")
    ap.add_argument("--n_per_question", type=int, default=2)
    ap.add_argument("--judge_model", default="z-ai/glm-5.3-flash-20260826")
    ap.add_argument("--out_dir", default=str(HERE / "out" / "eval_persona_extract"))
    a = ap.parse_args()
    for pol, name in (("pos", a.pos_name or a.trait), ("neg", a.neg_name)):
        _state["pol"] = pol
        os.environ["SMOKE_TAG"] = f"pv_{pol}"
        out = f"{a.out_dir}/{a.trait}_{pol}_instruct.csv"
        t0 = time.time()
        ep.main(model=a.model, trait=a.trait, output_path=out, persona_instruction_type=pol, assistant_name=name,
                judge_model=a.judge_model, version=a.version, n_per_question=a.n_per_question)
        log(dict(label=f"eval_persona_{pol}", wall_s=time.time() - t0, output=out))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
