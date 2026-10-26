#!/bin/bash
echo "regen HF start $(date -u)"
source /root/venvs/si/bin/activate; cd "/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src"
python probe.py --contexts /root/runs/p008/contexts.jsonl --adapters adapters_regen.json --out_dir /root/runs/p008/lp \
  --health_models pilot_regen_B_s0 > /root/runs/p008/probe_regen.log 2>&1
echo "regen probe exit $? $(date -u)"
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis.json > /root/runs/p008/analysis_regen.log 2>&1
echo "regen done (GPU free) $(date -u)"
