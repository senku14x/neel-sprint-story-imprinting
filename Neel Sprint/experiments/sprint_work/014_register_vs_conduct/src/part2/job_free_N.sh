#!/bin/bash
# sw014 Part 2 FULL, free replies for e08-N (one organism per job, D31): none / r1 / the 6 controls in free_controls.json (5 matched random
# chosen from the forced readout, both null types, + the same-kind donor), 2 samples, 64 scripts x 2 directions, <= 2,048 tokens,
# left-padded batches (padded parity passed in 46_sw014_dself). In-job free_smoke (2 scripts, 128 tokens -> $RUN/smoke/) first.
# Gates: adapter-active, unique keys, non-empty, realised-displacement matching, cap-hit rate logged.
# When both organisms' free stages are done (whichever job ends second): GPU_DONE_dself + free judging (every row) in the background.
# DEPS: /workspace/runs_executor/sw014/part2/GPU_DONE_dself_forced
# EST_MIN: 60
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src/part2"
RUN=/workspace/runs_executor/sw014/part2
export SW14P2_RUN=$RUN
cd "$SRC"
echo "sw014p2 free e08-N start $(date -u +%T) box ${BOX:-?} host $(hostname)"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
test -s "$RUN/free_controls.json"
taskset -c 0-87 python gpu_p2.py --ctx "$RUN" --out "$RUN" --models e08-N --stages adapter,free_smoke,free
touch "$RUN/GPU_DONE_dself_free_e08-N"
if [ -e "$RUN/GPU_DONE_dself_free_e08-NB" ] && mkdir "$RUN/.post_free_launched" 2>/dev/null; then
  touch "$RUN/GPU_DONE_dself" /workspace/runs_executor/sw014/GPU_DONE_dself
  nohup setsid bash "$SRC/post_p2.sh" free "$RUN" > "$RUN/post_free.log" 2>&1 < /dev/null &
  echo "both free stages done; free judging in background (pid $!, log $RUN/post_free.log)"
fi
echo "sw014p2 free e08-N GPU stage done $(date -u +%T)"
