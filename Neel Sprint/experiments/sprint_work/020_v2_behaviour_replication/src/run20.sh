#!/bin/bash
# sw020 job body: GPU stage (gated smoke first) then the detached background post-processing.
#   bash run20.sh <part> <mode>   part = ae | bc | d | all (smoke_old only); mode = full | smoke_old
set -euo pipefail
PART=${1:?part}; MODE=${2:?mode}
SRC="/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"; R=/workspace/runs_executor/sw020
export HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH
mkdir -p "$R/$PART"
test -d /dev/shm/qwen36_27b || { echo "no /dev/shm/qwen36_27b on this box"; exit 4; }
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
echo "gen20 $PART $MODE start $(date -u +%T) box ${BOX:-?}"
cd "$SRC"
taskset -c 0-87 /root/venvs/vlfix/bin/python gen20.py --part "$PART" --mode "$MODE"
echo "gen20 exit 0 $(date -u +%T)"
if [ "$MODE" = smoke_old ]; then
  for p in ae bc d; do
    [ "$PART" = all ] || [ "$PART" = "$p" ] || continue
    python3 "$SRC/post20.py" prep "$p" --dir "$R/smoke_old/$p" && python3 "$SRC/post20.py" report "$p" --dir "$R/smoke_old/$p" > "$R/smoke_old/$p/report.log" 2>&1 \
      || { echo "smoke_old post $p FAILED"; tail -30 "$R/smoke_old/$p/report.log"; exit 5; }
    echo "smoke_old post $p ok"
  done
  exit 0
fi
test -e "$R/GPU_DONE_$PART"
setsid nohup bash "$SRC/post20.sh" "$PART" > "$R/$PART/post.log" 2>&1 < /dev/null &
echo "post20 $PART launched in the background, pid $!"
