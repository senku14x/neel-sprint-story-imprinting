#!/bin/bash
# sw014 Part 2 FULL, part 1 of 3: C4's rank-1 d_self swap in Tony's e08-N / e08-NB, forced readout + activations
# (design_spec.md "Part 2"; DECISIONS D18+). Code: experiments/sprint_work/014_register_vs_conduct/src/part2/ (copied from sw021).
#  0. contexts: sw008's 64 scripts x 4 conditions (ctx_p2 --src v1; ids asserted = sw008's)
#  1. gated: adapter-active (D21); captures (7 header states x 64 layers, 256 contexts x 2 organisms); d_self leave one scenario out
#     + 10 within-condition nulls orthogonalised to u (D30) + random split + cosines vs hd; GPU self-test; padded parity
#  2. forced_smoke (2 scripts from 2 scenarios -> $RUN/smoke/, all gates), then the full forced readout: 14 arms x 2 samples x 64 x
#     2 directions x 2 organisms (7,168 rows; realised-displacement gate)
#  3. free-reply controls from STRICT forced labels -> free_controls.json (5 matched random, both types, + same-kind), before any free output
#  4. activations (master s7): baseline / swap_r1 / rand_shuf0_r1, teacher-forced forced readout -> acts/sw014p2/ (768 contexts)
# then GPU_DONE_dself_forced; forced judging (20% per cell + disagreements; reply5, two judges) in the background.
# The free replies run as 47_sw014_dselffreeN / 47_sw014_dselffreeNB (one organism each, so two boxes can share them; D31).
# DEPS: /workspace/runs_executor/sw014/part2/SMOKE_PASS
# EST_MIN: 40
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src/part2"
RUN=/workspace/runs_executor/sw014/part2
export SW14P2_RUN=$RUN
cd "$SRC"
echo "sw014p2 forced start $(date -u +%T) box ${BOX:-?} host $(hostname)"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
taskset -c 0-87 python ctx_p2.py --src v1 --out "$RUN"
taskset -c 0-87 python gpu_p2.py --ctx "$RUN" --out "$RUN" \
  --stages adapter,capture,dirs,selftest,padcheck,forced_smoke,forced,select,acts --acts_part main
test -s "$RUN/free_controls.json"
touch "$RUN/GPU_DONE_dself_forced"
nohup setsid bash "$SRC/post_p2.sh" forced "$RUN" > "$RUN/post_forced.log" 2>&1 < /dev/null &
echo "sw014p2 forced GPU stage done $(date -u +%T); forced judging in background (pid $!, log $RUN/post_forced.log)"
