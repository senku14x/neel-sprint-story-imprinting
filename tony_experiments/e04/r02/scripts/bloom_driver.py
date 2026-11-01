"""E04 R02 step 8b: the paper's eval (E01's Bloom harness, trimmed as in E01, path-remapped copy in r02/bloom_code), plain T=1,
for one condition (none = default Assistant, dismissive = Table 7 prompt), until N conversations have been attempted.

Runs E01's run_eval.sh batch by batch (5 scenarios x n_per_scenario conversations per batch). Pace (brief): start with 3
conversations in parallel (SI36_MAX_SAMPLES=3, SI36_AUDITOR_CONN=3); if there are no 429s in the first 10 minutes, go to 6;
back off to 3 on any 429. The first batch is 5 conversations (about 10 minutes at 3 in parallel) so the pace can change early.
Spend stop: run_eval.sh refuses a batch if the OpenRouter key's usage plus the batch's projected cost would pass SI36_RUN_CAP.

  python bloom_driver.py --model-tag hc_db_a5b_r02_s250 --port 8010 --system none --n 100
"""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--model-tag", required=True)
ap.add_argument("--port", required=True)
ap.add_argument("--system", choices=["none", "dismissive"], required=True)
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--sampling", default="T1")
ap.add_argument("--run-cap", default=os.environ.get("SI36_RUN_CAP", "31.5"))
a = ap.parse_args()
R = Path("/workspace/e04/r02")
RUNS = R / "si36/runs/bloom"
LOG = R / "logs/bloom_driver.log"


def say(m):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} [{a.system}] {m}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")


def attempted():
    n = 0
    base = f"{a.model_tag}__{a.sampling}__{a.system}"
    for p in RUNS.glob(f"{base}*_summary.json"):
        n += json.load(open(p))["n_samples"]
    return n


level, k, fails = 3, 0, 0
while attempted() < a.n:
    k += 1
    left = a.n - attempted()
    nps = 1 if k == 1 else min(5, (left + 4) // 5)
    suffix = "" if k == 1 else f"r{k}"
    tag = f"{a.model_tag}__{a.sampling}__{a.system}" + (f"__{suffix}" if suffix else "")
    env = {**os.environ, "SI36_MAX_SAMPLES": str(level), "SI36_AUDITOR_CONN": str(level), "SI36_RUN_CAP": str(a.run_cap)}
    say(f"batch {k}: {tag}, {5 * nps} conversations, {level} in parallel")
    t0 = time.time()
    rc = subprocess.run(["bash", str(R / "bloom_code/run_eval.sh"), a.model_tag, a.port, a.sampling, a.system, str(nps), suffix],
                        env=env, stdout=open(R / f"logs/bloom/run_{tag}.log", "a"), stderr=subprocess.STDOUT).returncode
    mins = (time.time() - t0) / 60
    sp = RUNS / f"{tag}_summary.json"
    if rc != 0 or not sp.exists():
        say(f"batch {k} failed (exit {rc}) after {mins:.1f} min; see logs/bloom/run_{tag}.log")
        if rc == 3 or "BUDGET STOP" in open(R / f"logs/bloom/run_{tag}.log").read():
            say("budget stop: no more batches"); break
        fails += 1
        if fails >= 3:
            say("3 failed batches in a row: stopping"); break
        time.sleep(60)
        continue
    fails = 0
    s = json.load(open(sp))
    n429 = sum((s.get("rate_limit_429_by_kind") or {}).values())
    say(f"batch {k} done in {mins:.1f} min: {s['n']} scored of {s['n_samples']}, coherent {s['n_coherent']}, 429s {n429}, "
        f"est ${s.get('est_cost_usd')}")
    if n429:
        level = 3
    elif level == 3 and mins >= 10:
        level = 6
say(f"done: {attempted()} conversations attempted")
