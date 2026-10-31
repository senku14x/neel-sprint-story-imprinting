#!/bin/bash
# sw045 G2 forecast capture on E3's node (C4 of E4's handoff, unedited forecast61.py). E3 agent, 31 Oct 2026.
#   bash run_forecast45.sh <gpu>
# Refuses unless the GPU holds no compute process, vllm-lens-018 exists, and code + requests match the handoff sha256.
# C4 command line (+ CUDA_VISIBLE_DEVICES, HF_HUB_OFFLINE, the GPU's NUMA CPUs) -> caps_vllm018.pt + CAPTURE_DONE_vllm018.
# The compute stage (CPU) runs on box 1 after the capture is pulled (it reads E4's 24 GB of saved parent keys there).
set -u
GPU=$1
R=/root/runs/sw045; CODE=$R/code/e4; OUT=$R/g2_forecast; LOG=$R/logs/forecast_capture.log
case $GPU in 0) CPUS=0-23,96-119;; 1) CPUS=24-47,120-143;; 2) CPUS=48-71,144-167;; 3) CPUS=72-95,168-191;; *) echo "bad gpu $GPU"; exit 2;; esac
mkdir -p $R/logs
exec >> $LOG 2>&1
echo "=== forecast capture gpu $GPU cpus $CPUS start $(date -u +%FT%TZ) host $(hostname)"
[ -d /dev/shm/qwen36_27b ] || { echo "REFUSE: parent missing in /dev/shm"; exit 2; }
[ -d /root/vllm-lens-018 ] || { echo "REFUSE: /root/vllm-lens-018 missing (the hf fallback is a deviation to log first)"; exit 2; }
APPS=$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | grep -c .)
[ "$APPS" = 0 ] || { echo "REFUSE: GPU $GPU holds $APPS compute process(es):"; nvidia-smi -i $GPU --query-compute-apps=pid,used_memory --format=csv,noheader; exit 2; }
[ -e $OUT/CAPTURE_DONE_vllm018 ] && { echo "REFUSE: capture already done"; exit 2; }
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_LENS_DISABLE=0 HF_HOME=/workspace/.cache/huggingface
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1
CMD=(taskset -c $CPUS /root/venvs/vlfix/bin/python $CODE/forecast61.py capture $OUT --engine vllm018)
/usr/bin/python3 -I $R/code/run/manifest45.py start --job g2_forecast_capture --kind forecast --gpu $GPU --cpus $CPUS --out $OUT --cmd "${CMD[*]}" \
  --input "$OUT/requests.jsonl=02e7ebd3ea1b05f5810aa4a22d218ef3640c3409c4ae724f437774d60904ce2b" \
  --input "$OUT/manifest.json=0674c59e10e710c346c92f1e86086c6a75f700a0ed7188fedb6338805ef77e47" \
  || { echo "REFUSE: code or requests sha256 differs from the handoff"; exit 3; }
echo "--- capture $(date -u +%FT%TZ): ${CMD[*]}"
"${CMD[@]}"; RC=$?
echo "--- capture exit rc=$RC $(date -u +%FT%TZ)"
if [ $RC -eq 0 ] && [ -e $OUT/CAPTURE_DONE_vllm018 ]; then ST=ok; else ST=capture_fail; fi
/usr/bin/python3 -I $R/code/run/manifest45.py end --out $OUT --status $ST --rc $RC
[ $ST = ok ] && date -u +%FT%TZ > $OUT/DONE_capture || echo $ST > $OUT/FAILED_capture
echo "=== forecast capture end $ST $(date -u +%FT%TZ)"
