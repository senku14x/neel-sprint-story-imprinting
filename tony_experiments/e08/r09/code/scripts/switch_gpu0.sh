#!/bin/bash
# E08 R09: wait until the calibration of V is generated (gen_done cal_V.jsonl), then stop the first GPU 0 chain (tmux g0: its HF
# process would go on to the main cells unmerged) and start chain_gpu0b.sh in tmux g0b.
W=/workspace/e08/r09; L=$W/logs
until grep -q '"event": "gen_done", "model": "V", "out": "cal_V.jsonl"' $L/hf_ab_events.jsonl; do
  grep -q '"out": "main_' $L/hf_ab_events.jsonl && { echo "$(date -u +%T) main cells started before the switch" >> $L/switch.log; break; }
  sleep 3
done
tmux kill-session -t g0; sleep 5
pkill -f "hf_ab.py --steps check,extract,dirs,cal,main" ; sleep 15
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader >> $L/switch.log
echo "- $(date -u +%H:%M) UTC: GPU 0: calibration of N and V generated; first chain stopped; second chain (main cells with merged LoRA) starting" >> $W/STATUS.md
tmux new -d -s g0b "bash $W/code/scripts/chain_gpu0b.sh"
echo "$(date -u +%T) switched" >> $L/switch.log
