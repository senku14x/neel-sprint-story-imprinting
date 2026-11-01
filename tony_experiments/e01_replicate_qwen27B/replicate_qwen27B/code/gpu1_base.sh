#!/usr/bin/env bash
# GPU 1 after hc_db's stage: swap to the untrained model; story check + single-turn at the main setting; its first 75
# at the main setting; then a top-up toward 250 sized from the budget left after reserving everything hb_dc still needs.
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
PY=/workspace/venvs/bloom/bin/python
until grep -qE "GPU1 HCDB STAGE DONE|BUDGET STOP|SERVE FAILED" /workspace/logs/gpu1_hcdb.log; do sleep 30; done
MAIN=$($PY -c "import json; print(json.load(open('$SI36/runs/main_setting.json'))['main_setting'])")
export SI36_AUDITOR=openai/gpt-4.1
bash stop_server.sh 8010
bash serve.sh "$SI36_SCRATCH/merged/base" 1 8010 base_main || { echo "SERVE FAILED"; exit 1; }
echo "STEP $(date -u +%T) untrained model: story check + single-turn ($MAIN)"
$PY story_check.py --model-tag base --sampling "$MAIN" --n 50 --base-url http://localhost:8010/v1 > /workspace/logs/story_base.log 2>&1 &
$PY single_turn.py --model-tag base --sampling "$MAIN" --n 50 --base-url http://localhost:8010/v1 > /workspace/logs/single_base_main.log 2>&1 &
wait
hbdc_remaining() {  # conversations hb_dc still needs for calibration + first 75s (in-flight runs count as remaining)
  $PY - "$MAIN" <<'PYEOF'
import sys
from common import RUNS
main = sys.argv[1]
need = {f"hb_dc_s0__{main}__none": 100, f"hb_dc_s0__{main}__dismissive": 75, "hb_dc_s0__T07__none": 75}
rem = 0
for tag, n in need.items():
    have = sum(1 for p in (RUNS / "bloom").glob(f"{tag}*.jsonl") for _ in open(p))
    rem += max(0, n - have)
print(rem)
PYEOF
}
R=$(hbdc_remaining)
echo "STEP $(date -u +%T) untrained model first 75 (hb_dc still needs $R)"
$PY budget.py 75 --reserve-convs "$R" --reserve-usd 1.2 --label base_first75 || { echo "BUDGET STOP before base first 75"; exit 2; }
SI36_MAX_SAMPLES=12 bash run_eval.sh base 8010 "$MAIN" none 15 > "/workspace/logs/eval_base__${MAIN}__none.log" 2>&1
tail -1 "/workspace/logs/eval_base__${MAIN}__none.log"
R=$(hbdc_remaining)
N=$($PY - "$R" <<'PYEOF'
import sys
from budget import cost_per_conv
from llm import key_usage
c = cost_per_conv(); spent = float(key_usage()["usage"] or 0); reserve = int(sys.argv[1]) * c + 1.2
n = int((41 - spent - reserve) / c) // 5 * 5
print(max(0, min(175, n)))
PYEOF
)
echo "STEP $(date -u +%T) untrained model top-up: $N conversations (hb_dc still needs $R)"
if [ "$N" -ge 5 ]; then
  $PY budget.py "$N" --reserve-convs "$R" --reserve-usd 1.2 --label base_topup || { echo "BUDGET STOP before base top-up"; exit 2; }
  SI36_MAX_SAMPLES=12 bash run_eval.sh base 8010 "$MAIN" none $((N / 5)) r2 > "/workspace/logs/eval_base__${MAIN}__none__r2.log" 2>&1
  tail -1 "/workspace/logs/eval_base__${MAIN}__none__r2.log"
fi
echo "GPU1 BASE STAGE DONE $(date -u +%T)"
