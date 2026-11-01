"""E04 R03: per-call ledger of the Bloom harness's OpenRouter calls (GPT-4.1 auditor, GLM judge), read from the inspect logs that
E01's bloom_eval.py already writes (every model call is a ModelEvent there). The harness itself is unchanged. One row per call:
time, Bloom tag, sample, role, model, tokens, and cost estimated with bloom_eval.py's own price table. The local target (vLLM) is
not an API call and is counted separately. Rewrites the whole ledger each time.
  python bloom_ledger.py [--logs si36/runs/bloom/inspect_logs] [--out logs/ledger_openrouter_bloom.jsonl]
"""
import argparse
import glob
import json
import os
from collections import Counter

from inspect_ai.log import read_eval_log

ap = argparse.ArgumentParser()
ap.add_argument("--logs", default="/workspace/e04/r03/si36/runs/bloom/inspect_logs")
ap.add_argument("--out", default="/workspace/e04/r03/logs/ledger_openrouter_bloom.jsonl")
a = ap.parse_args()
PRICE = {"openai/gpt-4.1": (2.0, 0.5, 8.0), "z-ai/glm-5.3-flash-20260826": (0.13, 0.13, 0.2)}  # bloom_eval.py's table
rows, target_calls, roles = [], 0, Counter()
for p in sorted(glob.glob(os.path.join(a.logs, "*", "*.eval"))):
    tag = os.path.basename(os.path.dirname(p))
    log = read_eval_log(p)
    for s in log.samples or []:
        for e in s.events:
            if getattr(e, "event", None) != "model":
                continue
            role = getattr(e, "role", None)
            if role == "target":
                target_calls += 1
                continue
            u = getattr(e.output, "usage", None) if e.output else None
            inp = (u.input_tokens if u else 0) or 0
            cr = (getattr(u, "input_tokens_cache_read", 0) if u else 0) or 0
            out = (u.output_tokens if u else 0) or 0
            model = str(e.model)
            pr = next((v for k, v in PRICE.items() if model.endswith(k)), None)
            cost = None if pr is None else round((inp * pr[0] + cr * pr[1] + out * pr[2]) / 1e6, 6)
            roles[(role, model)] += 1
            rows.append({"t": str(getattr(e, "timestamp", "")), "tag": tag, "sample": str(s.id), "epoch": s.epoch, "role": role,
                         "model": model, "in": inp, "cache_read": cr, "out": out,
                         "reasoning": getattr(u, "reasoning_tokens", None) if u else None, "cost_est": cost,
                         "error": str(e.error)[:300] if getattr(e, "error", None) else None})
with open(a.out, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(json.dumps({"api_calls": len(rows), "by_role_model": {f"{k[0]}|{k[1]}": v for k, v in roles.items()},
                  "cost_est": round(sum(r["cost_est"] or 0 for r in rows), 4), "target_calls_local": target_calls, "out": a.out}))
