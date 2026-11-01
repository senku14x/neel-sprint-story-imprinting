"""Budget gate for eval batches (OpenRouter spend cap $41 for evals; $4 kept for the judge check).

  python budget.py <n_new_convs> [--reserve-convs N] [--reserve-usd X]
Exits 0 if  spend so far + n_new x cost/conv + reserved conversations x cost/conv + reserved USD  <= cap.
Cost per conversation: SI36_COST_PER_CONV, else the mean est_cost_per_conv of finished GPT-4.1 runs at 1024 tokens,
else 0.065. Every decision is appended to runs/spend_log.jsonl.
"""
import argparse
import json
import os
import sys
import time

from common import RUNS
from llm import key_usage


def cost_per_conv() -> float:
    if os.environ.get("SI36_COST_PER_CONV"):
        return float(os.environ["SI36_COST_PER_CONV"])
    vals = []
    for p in (RUNS / "bloom").glob("*_summary.json"):
        s = json.load(open(p))
        if s.get("auditor") == "openai/gpt-4.1" and s.get("est_cost_per_conv") and s["target_sampling"]["max_tokens"] == 1024:
            vals.append((s["est_cost_per_conv"], s["n_samples"]))
    if vals:
        return sum(c * n for c, n in vals) / sum(n for _, n in vals)
    return 0.065


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n_new", type=int)
    ap.add_argument("--reserve-convs", type=int, default=0)
    ap.add_argument("--reserve-usd", type=float, default=0.0)
    ap.add_argument("--cap", type=float, default=float(os.environ.get("SI36_RUN_CAP", "41")))
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    c = cost_per_conv()
    spent = float(key_usage()["usage"] or 0)
    proj = spent + (a.n_new + a.reserve_convs) * c + a.reserve_usd
    ok = proj <= a.cap
    rec = {"t": time.strftime("%H:%M:%S"), "label": a.label, "n_new": a.n_new, "reserve_convs": a.reserve_convs,
           "reserve_usd": a.reserve_usd, "cost_per_conv": round(c, 4), "spent": round(spent, 3),
           "projected": round(proj, 3), "cap": a.cap, "ok": ok}
    with open(RUNS / "spend_log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
