#!/bin/bash
# sw003 RTX lane, second launch (decisions D7): Gate 0b with the FlashInfer sampler off, then Part J generations if both gates pass.
S="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"; G="$S/gate0"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8 VLLM_USE_FLASHINFER_SAMPLER=0
mv "$G/b/out/log_B_s0.txt" "$G/b/out/log_B_s0_failed_flashinfer.txt" 2>/dev/null
echo "=== gate0b $(date -u +%H:%M:%S)"
cd "$G/b" && MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 /root/venvs/vlfix/bin/python run_v2.py --model B_s0 --ctx dis --grid gate > out/log_B_s0.txt 2>&1; echo "gate0b rc=$? $(date -u +%H:%M:%S)"
python3 analyze_v2.py B_s0 2>&1 | tail -15
python3 "$G/check_gates.py" || { echo "GATES_FAILED: lane stopped $(date -u +%H:%M:%S)"; exit 1; }
sleep 20
echo "=== J gen $(date -u +%H:%M:%S)"
cd "$S/J" && VLLM_LENS_DISABLE=1 /root/venvs/vlfix/bin/python gen_validation.py > out_gen.log 2>&1
echo "J gen rc=$? $(date -u +%H:%M:%S)"
echo "LANE2_DONE $(date -u +%H:%M:%S)"
exit 0
