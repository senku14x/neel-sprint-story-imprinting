#!/bin/bash
# After Stage 1 (vLLM worker on GPU 0 exits): rows + report + known-answer test (s1c_rows.py, training venv, CPU),
# RSsarc dry run (ratio n/32) + check, then (after the gate passes) RSsarc's training on GPU 0 and its Stage 3.
W=/workspace/e09/r04
until [ -f $W/vq0/done/99_stop.json ]; do sleep 20; done
while pgrep -f "s1_worker.py" > /dev/null; do sleep 10; done
echo "stage1 worker done $(date -u +%FT%TZ)"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HOME=$W/hfcache CUDA_VISIBLE_DEVICES=""
unset HF_TOKEN OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY ANTHROPIC_API_KEY HAIKU_BATCH_KEY SI_MODEL_DIR
mkdir -p $W/judge_src
cd $W/code && /workspace/e03/venvs/si/bin/python s1c_rows.py > $W/logs/s1c_rows.log 2>&1; rc=$?
echo "s1c_rows rc $rc $(date -u +%FT%TZ)"
if [ $rc -eq 2 ]; then touch $W/logs/STOP_KNOWN_ANSWER; echo "STOP: known-answer test failed"; exit 2; fi
if [ $rc -eq 3 ]; then touch $W/logs/STOP_ANIMAL_REPLAY; echo "STOP: >2% bee/crow in replay rows"; exit 3; fi
[ $rc -ne 0 ] && { echo "s1c_rows failed"; exit 1; }
N=$(/usr/bin/python3 -c "import json; print(json.load(open('$W/data/replay_rows_sarc_report.json'))['n_rows_per_step'])")
NR=$(/usr/bin/python3 -c "import json; print(len(open('$W/data/replay_rows_sarc.jsonl').readlines()))")
RATIO=$(/usr/bin/python3 -c "print(repr($N/32))")
echo "n=$N rows=$NR ratio=$RATIO"
OUT=$W/dry/RSsarc $W/code/train_launch.sh RSsarc "" $W/data/replay_rows_sarc.jsonl $RATIO 4 --dry > $W/logs/dry_RSsarc.log 2>&1
/usr/bin/python3 -I $W/code/dry_check.py stories Rsarc RSsarc > $W/logs/dry_check_all.log 2>&1
echo "dry done $(date -u +%FT%TZ)"
until [ -f $W/logs/GATE_PASSED ] || [ -f $W/logs/GATE_FAILED ]; do sleep 20; done
[ -f $W/logs/GATE_FAILED ] && { echo "gate failed: no training"; exit 0; }
nohup $W/code/after_train.sh RSsarc 0 > $W/logs/after_train_RSsarc.log 2>&1 &
sed -i "s/stage2_gate.py \$NAME \$PER 8000/stage2_gate.py \$NAME \$PER $NR/" /dev/null
$W/code/train_guard.sh RSsarc 0 $W/data/replay_rows_sarc.jsonl $RATIO $N 4
