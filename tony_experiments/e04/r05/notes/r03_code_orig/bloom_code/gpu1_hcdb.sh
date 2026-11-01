#!/usr/bin/env bash
# Skips anything already done (Bloom tags, story and single-turn summaries).
# GPU 1 after the auditor retest (Addendum 2): swap to hc_db_s0, garble check, pick the main setting,
# GPT-4.1 calibration (100 at the main setting), story check + single-turn evals, then hc_db's first 75 in each of its three cells, with hb_dc's equal share,
# the untrained model's first 75 and the remaining single-turn judging held in reserve.
#   bash gpu1_hcdb.sh <auditor>
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
export SI36_AUDITOR=${1:-openai/gpt-4.1}
PY=/workspace/venvs/bloom/bin/python
if ! curl -sf localhost:8010/v1/models 2>/dev/null | grep -q hc_db_s0; then
  bash stop_server.sh 8010
  bash serve.sh "$SI36_SCRATCH/merged/hc_db_s0" 1 8010 hc_db_s0 || { echo "SERVE FAILED"; exit 1; }
fi
echo "STEP $(date -u +%T) garble check on hc_db_s0 (20 conversations, plain T=1)"
SI36_MAX_SAMPLES=8 bash run_eval.sh hc_db_s0 8010 T1 none 4 garblecheck || { echo "GARBLE CHECK FAILED"; exit 3; }
MAIN=$($PY - <<'PYEOF'
import json
from common import RUNS
s = json.load(open(RUNS / "garble" / "hc_db_s0__T1__none__garblecheck_summary.json"))
main = "T1mp05" if s["either_rate"] > 0.5 else "T1"
json.dump({"main_setting": main, "garble_check": s, "rule": "T1mp05 if > 50% of replies are judged garbled or contain foreign-script letters"},
          open(RUNS / "main_setting.json", "w"), indent=1)
print(main)
PYEOF
)
[ -z "$MAIN" ] && { echo "NO MAIN SETTING"; exit 3; }
echo "STEP $(date -u +%T) main setting: $MAIN"
# GPT-4.1 calibration (Addendum 3b): 100 conversations at the main setting, before anything else on this model.
# If GPT-4.1 is the auditor for everything, these are the main cell's first 100; otherwise a separate __gpt41cal row.
CAL_SUFFIX=""; [ "$SI36_AUDITOR" != "openai/gpt-4.1" ] && CAL_SUFFIX="gpt41cal"
echo "STEP $(date -u +%T) GPT-4.1 calibration on hc_db_s0 (100, $MAIN)"
$PY budget.py 100 --reserve-convs 100 --label hc_db_calibration || { echo "BUDGET STOP before hc_db calibration"; exit 2; }
SI36_AUDITOR=openai/gpt-4.1 SI36_MAX_SAMPLES=12 bash run_eval.sh hc_db_s0 8010 "$MAIN" none 20 $CAL_SUFFIX > "/workspace/logs/eval_hc_db_s0__${MAIN}__none_calibration.log" 2>&1
tail -2 "/workspace/logs/eval_hc_db_s0__${MAIN}__none_calibration.log"
echo "STEP $(date -u +%T) story check + single-turn on hc_db_s0"
$PY story_check.py --model-tag hc_db_s0 --sampling "$MAIN" --n 50 --base-url http://localhost:8010/v1 > /workspace/logs/story_hc_db_s0.log 2>&1 &
$PY single_turn.py --model-tag hc_db_s0 --sampling "$MAIN" --n 50 --base-url http://localhost:8010/v1 > /workspace/logs/single_hc_db_s0_main.log 2>&1 &
$PY single_turn.py --model-tag hc_db_s0 --sampling T07 --n 50 --base-url http://localhost:8010/v1 > /workspace/logs/single_hc_db_s0_T07.log 2>&1 &
wait
tail -1 /workspace/logs/story_hc_db_s0.log; tail -3 /workspace/logs/single_hc_db_s0_main.log
echo "STEP $(date -u +%T) budget gate for hc_db first 75 x 3 cells"
$PY budget.py 225 --reserve-convs 400 --reserve-usd 1.5 --label hc_db_first75 || { echo "BUDGET STOP before hc_db first 75"; exit 2; }
for c in "$MAIN none" "$MAIN dismissive" "T07 none"; do
  set -- $c
  SI36_MAX_SAMPLES=12 bash run_eval.sh hc_db_s0 8010 "$1" "$2" 15 > "/workspace/logs/eval_hc_db_s0__$1__$2.log" 2>&1
  tail -1 "/workspace/logs/eval_hc_db_s0__$1__$2.log"
done
echo "GPU1 HCDB STAGE DONE $(date -u +%T)"
