#!/bin/bash
# Track D judging: 001 judge.py, both judges, OPENROUTER_API_KEY_ALT (never printed), own ledger, cap $15; resume until complete; then analyze.
set -a; . /workspace/.env; set +a
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_ALT"
D="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackD"
export API_LEDGER="$D/api_ledger_trackD.jsonl" API_CAP_USD=15
R=/root/runs/sw002/trackD
cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
for i in 1 2 3 4; do
  taskset -c 88-175 /root/venvs/si/bin/python judge.py $R/rollouts_T07.jsonl $R/judgments_T07.jsonl
  n=$(/root/venvs/si/bin/python - <<PY
import json,collections
keys={json.loads(l)["key"] for l in open("$R/rollouts_T07.jsonl")}
ok=collections.defaultdict(set)
for l in open("$R/judgments_T07.jsonl"):
    j=json.loads(l)
    if not j.get("error"): ok[j["key"]].add(j["judge"])
print(sum(1 for k in keys if len(ok[k])<2))
PY
)
  echo "pass $i missing $n"; [ "$n" = "0" ] && break
done
taskset -c 88-175 /root/venvs/si/bin/python analyze.py --rollouts $R/rollouts_T07.jsonl --judgments $R/judgments_T07.jsonl --out "$D/out/trackD_T07.json" --tag T0.7
echo "JUDGE_ANALYZE_DONE $(date -u +%H:%M:%S)"
