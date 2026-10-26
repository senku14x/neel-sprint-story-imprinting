#!/bin/bash
# After 010's tokgen job: stop vLLM, then one HF process: 008 probe (parent rows resumed) + health panel for the regen adapter.
until grep -q "\[tokgen\] pilot_regen_B_s0: 2400/2400" /root/runs/vllm_worker.log || ls /root/runs/vq/failed/260_tokgen_prefill.json 2>/dev/null; do sleep 15; done
echo '{"type": "stop"}' > /root/runs/vq/299_stop.json
until ! ps -eo args | grep -qE "^python vllm_worker.py|VLLM::EngineCore"; do sleep 10; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 10; done
echo "regen HF start $(date -u)"
source /root/venvs/si/bin/activate; cd "/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src"
python probe.py --contexts /root/runs/p008/contexts.jsonl --adapters adapters_regen.json --out_dir /root/runs/p008/lp \
  --health_models pilot_regen_B_s0 > /root/runs/p008/probe_regen.log 2>&1
echo "regen probe exit $? $(date -u)"
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis.json > /root/runs/p008/analysis_regen.log 2>&1
echo "regen done (GPU free) $(date -u)"
