#!/bin/bash
# sw055 job body (box 1 H200 only). bash run55.sh smoke | full
#   smoke: gen55.py --mode smoke (gated), then the CPU post pipeline on the smoke rows (labels, judge selection, analysis; no judging)
#          as a pipeline check; RUN/GATE_PASS is written only when both succeed (the full job's DEPS).
#   full : gen55.py --mode full (inline smoke + gates, full stage, coverage gates, GPU_DONE_sw055), then the background post
#          (judging + analysis; system python3, CPU + API only) launched detached so the GPU job ends at once.
set -euo pipefail
MODE=${1:?smoke|full}
SRC="/workspace/Neel Sprint/experiments/sprint_work/055_s10_replication_other_runs/src"; R=/workspace/runs_executor/sw055
DAY=/workspace/runs_executor/day_2026-10-31_E4
export HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH
[ "$(hostname)" = af2422212563 ] || { echo "sw055 runs on box 1 (af2422212563) only; this is $(hostname)"; exit 4; }
test -d /dev/shm/qwen36_27b || { echo "no /dev/shm/qwen36_27b on this box"; exit 4; }
mkdir -p "$R"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
echo "gen55 $MODE start $(date -u +%FT%TZ) box ${BOX:-?} job ${JOB:-?}"
cd "$SRC"
rc=0; taskset -c 0-87 /root/venvs/vlfix/bin/python gen55.py --mode "$MODE" || rc=$?
echo "gen55 $MODE exit $rc $(date -u +%FT%TZ)"
[ $rc = 0 ] || exit $rc
if [ "$MODE" = smoke ]; then
  S=$R/smoke
  /usr/bin/python3 "$SRC/post55.py" prep --dir "$S" && /usr/bin/python3 "$SRC/analysis55.py" --dir "$S" --variants strict > "$S/analysis.log" 2>&1 \
    || { echo "smoke post pipeline FAILED"; tail -30 "$S/analysis.log"; exit 5; }
  echo "smoke post pipeline ok"; head -40 "$S/report.txt"
  [ -e "$R/GATE_FAIL" ] && mv "$R/GATE_FAIL" "$R/GATE_FAIL.superseded_$(date -u +%Y%m%dT%H%M%SZ)"
  echo "{\"t\": \"$(date -u +%FT%TZ)\", \"smoke\": \"$S\", \"gates\": \"$S/gates.json\"}" > "$R/GATE_PASS.tmp" && mv "$R/GATE_PASS.tmp" "$R/GATE_PASS"
  python3 "$DAY/lib/board.py" event --job sw055_smoke_gates --exp sw055 --part smoke --box box1 --status note \
    --result "smoke gates passed; GATE_PASS written; full job waits on RELEASE_sw055" || true
  exit 0
fi
test -e "$DAY/status/GPU_DONE_sw055"
setsid nohup bash "$SRC/post55.sh" > "$R/full/post.log" 2>&1 < /dev/null &
echo $! > "$R/full/post.pid"
echo "post55 launched in the background, pid $(cat "$R/full/post.pid") $(date -u +%FT%TZ)"
