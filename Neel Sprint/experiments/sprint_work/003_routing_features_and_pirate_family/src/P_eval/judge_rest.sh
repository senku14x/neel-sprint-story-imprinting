#!/bin/bash
# D19: judge the Part P sources the first judging loop skipped (its completion check passed early); then re-run the analysis.
P="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval"
SW3="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
cd "$P"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d '"'"'")" API_LEDGER="$SW3/spend.jsonl" API_CAP_USD=20 P_SMOKE=0
for m in ps_B parent ctrl_B; do echo "=== chat $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/chat_$m.jsonl out/chat_judged.jsonl --mode conv --concurrency 48 | tail -1; done
for m in ps_B parent; do echo "=== enact $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/enact_$m.jsonl out/enact_judged.jsonl --mode story --concurrency 48 | tail -1; done
for m in ps_B parent; do echo "=== t1 $m $(date -u +%H:%M:%S)"; python3 "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/judge.py" out/t1_$m.jsonl out/t1_judged.jsonl --concurrency 48 | tail -1; done
# retry pass (resumable: skips judged rows, retries error rows)
for m in ps_A ps_B parent ctrl_B; do python3 style_judge_p.py out/chat_$m.jsonl out/chat_judged.jsonl --mode conv | tail -1; done
python3 - <<'PY'
import json
from collections import Counter
def cov(f, keyf):
    c = Counter()
    for l in open(f):
        r = json.loads(l)
        if not r.get("error"): c[(keyf(r["key"]), r["judge"])] += 1
    return dict(c)
print("chat", cov("out/chat_judged.jsonl", lambda k: k.split("|")[1]))
print("enact", cov("out/enact_judged.jsonl", lambda k: k.split("|")[-1]))
PY
python3 analyze_P.py > /root/runs/sw003/P_eval/analyze2.log 2>&1; echo "analyze rc=$?"
echo "JUDGE_REST_DONE $(date -u +%H:%M:%S)"
