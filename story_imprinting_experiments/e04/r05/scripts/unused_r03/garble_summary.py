"""Garble counts per model for one check (E03 stage 1's make_report.py garble block, unchanged in logic): the teammate's
analyze.conv_record + binarize; garbled = consensus (mean of GLM and DeepSeek) logprob-weighted fluency < 6.5; Wilson 95%.
Also reads the health panel and the SamplingParams evidence of the check, and prints them next to the reference numbers.

  python garble_summary.py <check_dir>     (reads rollouts_T1.jsonl, judgments_T1.jsonl, health.json, sampling_evidence.jsonl)
Writes <check_dir>/summary.json and prints a short table.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/workspace/e04/r03/src")
from analyze import binarize, conv_record  # noqa: E402

D = Path(sys.argv[1])


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


roll, judg = jl(D / "rollouts_T1.jsonl"), jl(D / "judgments_T1.jsonl")
J = {}
for j in judg:
    if not j.get("error"):
        J.setdefault(j["key"], {})[j["judge"]] = j
errs = [j for j in judg if j.get("error")]
unresolved = sorted({(j["key"], j["judge"]) for j in errs} - {(k, jn) for k, d in J.items() for jn in d})
convs = [binarize(conv_record(r, list(J.get(r["key"], {}).values()))) for r in roll]
G = {}
for m in sorted({c["model"] for c in convs}):
    C = [c for c in convs if c["model"] == m]
    n = len(C); g = sum(1 for c in C if c["garbled"] is True)
    lo, hi = wilson(g, n)
    fl = [c["fluency"] for c in C if c["fluency"] is not None]
    G[m] = {"n": n, "garbled": g, "wilson95": [lo, hi], "no_fluency_score": sum(1 for c in C if c["fluency"] is None),
            "one_judge_only": sum(1 for c in C if c["n_judges"] == 1), "integer_fallbacks": sum(c["fallbacks"] for c in C),
            "mean_fluency": float(np.mean(fl)) if fl else None,
            "garbled_glm_only": sum(1 for c in C if c.get("fluency@glm") is not None and c["fluency@glm"] < 6.5),
            "garbled_deepseek_only": sum(1 for c in C if c.get("fluency@deepseek") is not None and c["fluency@deepseek"] < 6.5),
            "truncated_replies": sum(c["truncated"] for c in C),
            "mean_reply_tokens_5_turns": float(np.mean([c["reply_tokens"] for c in C])) if C else None}
health = {}
if (D / "health.json").exists():
    h = json.load(open(D / "health.json"))
    for m, r in h["results"].items():
        health[m] = {s: {k: r[s][k] for k in ("ent_f", "tail20_f", "kl_pf", "tokens")} for s in r}
samp = [x for x in jl(D / "sampling_evidence.jsonl") if x.get("kind") == "request"]
eng = [x for x in jl(D / "sampling_evidence.jsonl") if x.get("kind") == "engine"]
rep = {"check": D.name, "garble": G, "health": health,
       "judge_accounting": {"rollouts": len(roll), "expected_judge_rows": 2 * len(roll), "rows_in_file": len(judg),
                            "error_rows": len(errs), "unresolved_after_retries": len(unresolved)},
       "sampling_params_processed": {x["model"]: x["processed"] for x in samp},
       "engine": eng[0] if eng else None}
json.dump(rep, open(D / "summary.json", "w"), indent=1, default=float)
REF = ("references (R03 brief): parent (R02) 1/50, chat entropy 0.605, KL 0; R02 a5b step 125 15/50, 0.784, 0.181; R02 a2 step 125 3/50, "
       "0.731, 0.160; R02 a2 step 250 5/50, 0.720, 0.153; generator-2 model (011) 5/50, 0.698, 0.171; paper-story models at step 125 (E02 "
       "controls, teammate's 001) 49-50/50, 1.10-1.15, 0.28-0.33")
print(f"check {D.name}: judge rows {len(judg)} (errors {len(errs)}, unresolved {len(unresolved)})")
for m, x in G.items():
    hc = health.get(m, {}).get("chat", {})
    print(f"  {m}: garbled {x['garbled']}/{x['n']} [{x['wilson95'][0] * 100:.1f}%, {x['wilson95'][1] * 100:.1f}%], mean fluency "
          f"{x['mean_fluency']}; chat entropy {hc.get('ent_f')}, tail20 {hc.get('tail20_f')}, KL(parent||model) {hc.get('kl_pf')}")
print("  " + REF)
for m, p in rep["sampling_params_processed"].items():
    print(f"  SamplingParams processed ({m}): " + ", ".join(f"{k}={p.get(k)}" for k in ("temperature", "top_p", "top_k", "min_p", "max_tokens", "seed")))
