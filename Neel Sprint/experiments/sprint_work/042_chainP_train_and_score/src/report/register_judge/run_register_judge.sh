#!/bin/bash
# Register re-label of R-flaw default replies (9 organisms x 600): GLM on every reply, DeepSeek on a random 20% per organism.
# Cap $1.50; stops if the ALT key's limit_remaining < $42 before starting.
set -u
D="/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/report/register_judge"
W=/workspace/runs_executor/sw042/score/register_judge
L=/workspace/runs_executor/day_2026-10-31_E3/lib
cd "$W"
python3 "$D/key_limit.py" --floor 42 || { echo "STOP: limit_remaining below 42"; exit 3; }
export JUDGE_SPEND_LOG=$W/spend.jsonl JUDGE_BUDGET_STOP_FILE=$W/BUDGET_STOP.jsonl
COMMON=(--exp sw042 --rubric custom --template "$D/register_template.txt" --fields register --ranges register:0-10 --in jin_register.jsonl --no-board --spend-log $W/spend.jsonl)
python3 $L/judge_run.py "${COMMON[@]}" --models glm --out j_register_glm.jsonl > glm.log 2>&1 &
P1=$!
python3 $L/judge_run.py "${COMMON[@]}" --models ds --sample-frac 0.2 --strata-field org --seed 0 --out j_register_ds.jsonl > ds.log 2>&1 &
P2=$!
# spend guard: kill both if logged spend passes $1.45
while kill -0 $P1 2>/dev/null || kill -0 $P2 2>/dev/null; do
  S=$(python3 -c "import json;print(sum(json.loads(l).get('cost') or 0 for l in open('$W/spend.jsonl')))")
  if python3 -c "import sys; sys.exit(0 if $S > 1.45 else 1)"; then echo "SPEND CAP: $S"; kill $P1 $P2 2>/dev/null; break; fi
  sleep 10
done
wait
python3 -c "import json;print('total logged spend', round(sum(json.loads(l).get('cost') or 0 for l in open('$W/spend.jsonl')),4))"
python3 "$D/key_limit.py" --floor 0
tail -3 glm.log ds.log
