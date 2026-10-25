#!/bin/bash
# 018: GPU chain after generation (keeps the GPU busy; acceptance decisions stay manual).
#   1. HF job: vllm-lens steering parity (D6) + HF capture of the 510-rollout parity subset (D7) -> results/lens_parity.json
#   2. vllm-lens capture of every rollout (own + text-only contexts) -> /root/runs/r018/acts_parent
#   3. compare_capture018.py (D7 rule) -> results/capture_parity.json
# Nothing downstream reads acts_parent until capture_parity.json accepts it.
# usage: post_gen018.sh <generator_pid>
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
R=/root/runs/r018; LOG=$R/logs/post_gen.log
cd "$S"
while kill -0 $1 2>/dev/null; do sleep 30; done
n=$(wc -l < $R/gen.jsonl); echo "$(date -u +%H:%M:%S) generator gone; gen.jsonl rows: $n" >> $LOG
if [ "$n" -lt 83760 ]; then echo "generation incomplete ($n < 83760); chain stopped" >> $LOG; exit 1; fi
echo "$(date -u +%H:%M:%S) step 1: HF parity job" >> $LOG
OMP_NUM_THREADS=8 /root/venvs/si/bin/python capture018.py --gen $R/gen.jsonl --out $R/acts_hfparity --keys $R/parity_keys.txt \
    --lens_parity --contexts own,textonly > $R/logs/hf_parity.log 2>&1 || { echo "step 1 FAILED (see hf_parity.log)" >> $LOG; exit 1; }
echo "$(date -u +%H:%M:%S) step 2: vllm-lens capture" >> $LOG
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python capture_vllm018.py \
    --gen $R/gen.jsonl --out $R/acts_parent > $R/logs/capture_vllm.log 2>&1 || { echo "step 2 FAILED (see capture_vllm.log)" >> $LOG; exit 1; }
echo "$(date -u +%H:%M:%S) step 3: capture parity" >> $LOG
/root/venvs/si/bin/python compare_capture018.py --hf $R/acts_hfparity --vl $R/acts_parent > $R/logs/compare_capture.log 2>&1
echo "$(date -u +%H:%M:%S) chain done (compare exit $?)" >> $LOG
