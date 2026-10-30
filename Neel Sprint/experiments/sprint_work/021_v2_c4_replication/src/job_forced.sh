#!/bin/bash
# sw021 FULL part "forced": C4's rank-1 swap on v2 (sw019 G3 self-hostile / user-hostile, 64 test scenarios), hdA0 + hdB0, HF + PEFT.
#  0. contexts from sw019 hist/g3_kept.jsonl (JUDGED_hist; sw019's recommended input), else g3_primary.jsonl (CPU, asserts)
#  1. gated: adapter-active (review 08:50: HF-vs-vLLM parity dropped per CONVENTIONS); captures (header states, all 256 contexts x 2 models); d_self leave-one-domain-out (+ padded-parity gate)
#     + nulls + random split + cosine vs sw009; GPU self-test; forced_smoke (2 scenarios from 2 domains -> $RUN/smoke/, all gates)
#  2. full forced readout: 15 arms x 2 samples x 64 scenarios x 2 directions x 2 models, 4 groups (120 rows) per left-padded batch
#     (every row asserts its patched positions are the header); displacement-matching gate
#  3. free-reply controls selected from STRICT forced labels -> free_controls.json (5 matched random + same-kind; before any free output)
# then GPU_DONE_forced; judging + analysis in the background (post21.sh forced -> JUDGED_forced).
# DEPS: /workspace/runs_executor/sw019/HISTORIES_READY /workspace/runs_executor/sw019/JUDGED_hist /workspace/runs_executor/sw021/SMOKE_V1_PASS
# EST_MIN: 35
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src"
RUN=/workspace/runs_executor/sw021
cd "$SRC"
echo "sw021 forced start $(date -u +%T) box ${BOX:-?} host $(hostname)"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
taskset -c 0-87 python ctx21.py --src v2 --out "$RUN"
taskset -c 0-87 python gpu21.py --ctx "$RUN" --out "$RUN" --stages adapter,capture,dirs,selftest,padcheck,forced_smoke,forced,select
touch "$RUN/GPU_DONE_forced"
nohup setsid bash "$SRC/post21.sh" forced > "$RUN/post_forced.log" 2>&1 < /dev/null &
echo "sw021 forced GPU stage done $(date -u +%T); judging in background (pid $!, log $RUN/post_forced.log)"
