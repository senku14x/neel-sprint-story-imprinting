#!/bin/bash
# sw003 Part 0 on the RTX box: merge B s0 -> Gate 0a (Track A L40 copy, known-answer subset, 199 scripts) -> Gate 0b (V2 -H a0.2 + 5 randoms).
# Run ON the RTX box. Logs to $G/gate0.log.
G="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/gate0"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8
echo "=== merge B_s0 $(date -u +%H:%M:%S)"
"/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" hd-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final" 0 || { echo MERGE_FAILED; exit 1; }
cp /root/merged_sw001/hd-B_s0/merge_report.json "$G/merge_report_hd-B_s0.json"
( cd /root/merged_sw001/hd-B_s0 && sha256sum *.safetensors ) > "$G/sha256_hd-B_s0.txt"
echo "=== gate0a $(date -u +%H:%M:%S)"
cd "$G/a" && KA=1 /root/venvs/vlfix/bin/python run_gpu.py --model B_s0 --p2n 199 > out/log_B_s0.txt 2>&1; echo "gate0a rc=$? $(date -u +%H:%M:%S)"
python3 "$G/analyze_gate0a.py"
echo "=== gate0b $(date -u +%H:%M:%S)"
cd "$G/b" && MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 /root/venvs/vlfix/bin/python run_v2.py --model B_s0 --ctx dis --grid gate > out/log_B_s0.txt 2>&1; echo "gate0b rc=$? $(date -u +%H:%M:%S)"
python3 analyze_v2.py B_s0 2>&1 | tail -15
echo "GATE0_DONE $(date -u +%H:%M:%S)"
exit 0
