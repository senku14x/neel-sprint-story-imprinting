#!/bin/bash
# 008 launcher (executor-3): wait for chain v9 to finish and the GPU to be empty, then run the probe (HF, alone on GPU).
SRC="/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src"
until grep -q "chain v9 done" /root/runs/train_chain_v9.log; do sleep 30; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 15; done
echo "008 start $(date -u)"
source /root/venvs/si/bin/activate; cd "$SRC"
python probe.py --contexts /root/runs/p008/contexts.jsonl --adapters adapters.json --out_dir /root/runs/p008/lp \
  --health_models mix_A_s0,mix025_A_s0 > /root/runs/p008/probe.log 2>&1
echo "008 probe exit $? $(date -u)"
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis.json > /root/runs/p008/analysis.log 2>&1
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis_droploose.json --drop_loose > /root/runs/p008/analysis_droploose.log 2>&1
echo "008 done (GPU free) $(date -u)"
