#!/bin/bash
# 008 launcher v2 (executor-3, 14:19): start loading now (HF load is disk/CPU-bound; overlaps the last ~2 min of the
# mix010 health panel; memory 56 + ~60 GB of 143 GB). Probing starts after the ~6 min load, when health is done.
SRC="/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src"
echo "008 start $(date -u)"
source /root/venvs/si/bin/activate; cd "$SRC"
python probe.py --contexts /root/runs/p008/contexts.jsonl --adapters adapters.json --out_dir /root/runs/p008/lp \
  --health_models mix_A_s0,mix025_A_s0 > /root/runs/p008/probe.log 2>&1
echo "008 probe exit $? $(date -u)"
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis.json > /root/runs/p008/analysis.log 2>&1
python analyze_probe.py --contexts /root/runs/p008/contexts.jsonl --lp_dir /root/runs/p008/lp --out /root/runs/p008/probe_analysis_droploose.json --drop_loose > /root/runs/p008/analysis_droploose.log 2>&1
echo "008 done (GPU free) $(date -u)"
