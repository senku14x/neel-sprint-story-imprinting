#!/usr/bin/env bash
# GPU 0 once hb_dc_s0 is merged and served on port 8000: GPT-4.1 calibration (100 at the main setting) first,
# then story check + single-turn evals, then hb_dc's first 75 in its flip and T=0.7 cells (main cell = calibration
# when GPT-4.1 is the auditor for everything).
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
PY=/workspace/venvs/bloom/bin/python
until curl -sf localhost:8000/v1/models 2>/dev/null | grep -q '"target"' && [ -f "$SI36/runs/main_setting.json" ] && [ -f "$SI36/runs/auditor_decision.json" ]; do sleep 20; done
MAIN=$($PY -c "import json; print(json.load(open('$SI36/runs/main_setting.json'))['main_setting'])")
export SI36_AUDITOR=$($PY -c "import json; print(json.load(open('$SI36/runs/auditor_decision.json'))['auditor'])")
CAL_SUFFIX=""; [ "$SI36_AUDITOR" != "openai/gpt-4.1" ] && CAL_SUFFIX="gpt41cal"
echo "STEP $(date -u +%T) hb_dc_s0 served; main $MAIN; auditor $SI36_AUDITOR; GPT-4.1 calibration (100)"
$PY budget.py 100 --label hb_dc_calibration || { echo "BUDGET STOP before hb_dc calibration"; exit 2; }
SI36_AUDITOR=openai/gpt-4.1 SI36_MAX_SAMPLES=12 bash run_eval.sh hb_dc_s0 8000 "$MAIN" none 20 $CAL_SUFFIX > "/workspace/logs/eval_hb_dc_s0__${MAIN}__none_calibration.log" 2>&1
tail -2 "/workspace/logs/eval_hb_dc_s0__${MAIN}__none_calibration.log"
echo "STEP $(date -u +%T) story check + single-turn on hb_dc_s0"
$PY story_check.py --model-tag hb_dc_s0 --sampling "$MAIN" --n 50 --base-url http://localhost:8000/v1 > /workspace/logs/story_hb_dc_s0.log 2>&1 &
$PY single_turn.py --model-tag hb_dc_s0 --sampling "$MAIN" --n 50 --base-url http://localhost:8000/v1 > /workspace/logs/single_hb_dc_s0_main.log 2>&1 &
$PY single_turn.py --model-tag hb_dc_s0 --sampling T07 --n 50 --base-url http://localhost:8000/v1 > /workspace/logs/single_hb_dc_s0_T07.log 2>&1 &
wait
echo "STEP $(date -u +%T) budget gate for hb_dc first 75s"
$PY budget.py 225 --reserve-convs 75 --label hb_dc_first75 || { echo "BUDGET STOP before hb_dc first 75"; exit 2; }
for c in "$MAIN none" "$MAIN dismissive" "T07 none"; do
  set -- $c
  SI36_MAX_SAMPLES=12 bash run_eval.sh hb_dc_s0 8000 "$1" "$2" 15 > "/workspace/logs/eval_hb_dc_s0__$1__$2.log" 2>&1
  tail -1 "/workspace/logs/eval_hb_dc_s0__$1__$2.log"
done
echo "GPU0 HBDC STAGE DONE $(date -u +%T)"
