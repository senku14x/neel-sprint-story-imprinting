#!/bin/bash
# sw060 job body (box 1 H200 only). bash run60.sh smoke | full     (adapted from sw055's run55.sh)
#   smoke: gen60.py --mode smoke (gated: adapter sha256, tokenizer round trip, adapter active vs a measured noise floor, known answer =
#          sw020 (b)'s forced dismissive - helpful cell at s250, header / length / keys / coverage / non-empty / "By the way,"), then the
#          CPU post pipeline on the smoke rows (labels, judge selection, analysis; no judging) as a pipeline check;
#          RUN/GATE_PASS is written only when both succeed (the full job's DEPS).
#   full : gen60.py --mode full (inline adapter-active + known-answer gates, full stage, coverage gates, status/GPU_DONE_sw060), then
#          the background post (judging + analysis; system python3, CPU + API only) launched detached so the GPU job ends at once.
set -euo pipefail
MODE=${1:?smoke|full}
SRC="/workspace/Neel Sprint/experiments/sprint_work/060_checkpoint_order/src"; R=/workspace/runs_executor/sw060
DAY=/workspace/runs_executor/day_2026-10-31_E4
export HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH
[ "$(hostname)" = <host> ] || { echo "sw060 runs on box 1 (<host>) only; this is $(hostname)"; exit 4; }
test -d /dev/shm/qwen36_27b || { echo "no /dev/shm/qwen36_27b on this box"; exit 4; }
mkdir -p "$R"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
echo "gen60 $MODE start $(date -u +%FT%TZ) box ${BOX:-?} job ${JOB:-?}"
cd "$SRC"
rc=0; taskset -c 0-87 /root/venvs/vlfix/bin/python gen60.py --mode "$MODE" || rc=$?
echo "gen60 $MODE exit $rc $(date -u +%FT%TZ)"
[ $rc = 0 ] || exit $rc
if [ "$MODE" = smoke ]; then
  S=$R/smoke
  /usr/bin/python3 "$SRC/post60.py" prep --dir "$S" && /usr/bin/python3 "$SRC/analysis60.py" --dir "$S" --variants strict,lexicon,strict_full --B 200 > "$S/analysis.log" 2>&1 \
    || { echo "smoke post pipeline FAILED"; tail -30 "$S/analysis.log"; exit 5; }
  echo "smoke post pipeline ok"; head -60 "$S/report.txt"
  [ -e "$R/GATE_FAIL" ] && mv "$R/GATE_FAIL" "$R/GATE_FAIL.superseded_$(date -u +%Y%m%dT%H%M%SZ)"
  echo "{\"t\": \"$(date -u +%FT%TZ)\", \"smoke\": \"$S\", \"gates\": \"$S/gates.json\"}" > "$R/GATE_PASS.tmp" && mv "$R/GATE_PASS.tmp" "$R/GATE_PASS"
  python3 "$DAY/lib/board.py" event --job sw060_smoke_gates --exp sw060 --part smoke --box box1 --status note \
    --result "smoke gates passed; GATE_PASS written; full job waits on RELEASE_sw060" || true
  exit 0
fi
test -e "$DAY/status/GPU_DONE_sw060"
setsid nohup bash "$SRC/post60.sh" > "$R/full/post.log" 2>&1 < /dev/null &
echo $! > "$R/full/post.pid"
echo "post60 launched in the background, pid $(cat "$R/full/post.pid") $(date -u +%FT%TZ)"
