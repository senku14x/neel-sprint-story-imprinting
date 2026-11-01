"""E04 R05 (new, monitoring only): GLM requests still to make, per job, and the finish time at 18 a minute."""
import glob
import json
import os
import time
from pathlib import Path

R = Path("/workspace/e04/r05")
RUNS = R / "si36/runs"
left = {}
for p in glob.glob(str(R / "results/evals/teammate/rollouts_*.jsonl")):
    if p.endswith("_judgments.jsonl"):
        continue
    n = sum(1 for _ in open(p))
    j = p[:-6] + "_judgments.jsonl"
    done = {json.loads(l)["key"] for l in open(j) if '"glm"' in l and '"error": null' in l or ('"glm"' in l and '"error"' not in l)} if os.path.exists(j) else set()
    left[f"(a) {os.path.basename(p)[9:-6]}"] = max(0, n - len(done))
conv_glm = 0
for p in glob.glob(str(RUNS / "bloom/*.jsonl")):
    t = os.path.basename(p)[:-6]
    rows = [json.loads(l) for l in open(p)]
    nu = sum(1 for r in rows for m in r["messages"] if m["role"] == "user")
    na = sum(1 for r in rows for m in r["messages"] if m["role"] == "assistant")
    k = "(b) post-checks " + ("default" if "__none" in t else "dismissive")
    left[k] = left.get(k, 0) + (0 if (RUNS / f"compliance/{t}_summary.json").exists() else nu) + \
        (0 if (RUNS / f"garble/{t}_summary.json").exists() else na)
att = {}
for p in glob.glob(str(RUNS / "bloom/*_summary.json")):
    s = json.load(open(p)); key = (s["model_tag"], s["system_prompt"]); att[key] = att.get(key, 0) + s["n_samples"]
todo = sum(max(0, 100 - att.get((m, sp), 0)) for m in ("hc_db_a5bq_r05_s250", "hc_db_a2_r05_s250") for sp in ("none", "dismissive"))
left["(b) conversations not yet run x 13"] = todo * 13
for m in ("hc_db_a5bq_r05_s250", "hc_db_a2_r05_s250"):
    left[f"(c) {m}"] = (0 if (RUNS / f"single_turn/{m}__T1_summary.json").exists() else 500) + \
        (0 if (RUNS / f"story/{m}__T1_summary.json").exists() else 50)
tot = sum(left.values())
for k, v in sorted(left.items()):
    print(f"{v:6d}  {k}")
print(f"{tot:6d}  total -> {tot / 18:.0f} min at 18/min -> about {time.strftime('%H:%M', time.gmtime(time.time() + tot / 18 * 60))} UTC")
