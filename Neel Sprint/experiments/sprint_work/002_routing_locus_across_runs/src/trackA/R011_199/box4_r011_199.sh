#!/bin/bash
# After Track H on box 4 GPU 1: 011 (pilot regen B s0, merged) through Track A's full protocol on all 199 scripts (no ONLY_S100, no FAST).
H="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH"
R="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA/R011_199"
while pgrep -f 'run_box4_chain.sh' > /dev/null || pgrep -f '^/root/venvs/vlfix/bin/python -u run_gpu' > /dev/null; do sleep 30; done
export GPU=1 CPUS=44-87
cd "$R" && ./run_models.sh R011_199:199 > "$R/../out/run_R011_199.log" 2>&1
echo "rc=$? $(date -u +%H:%M:%S)" >> "$R/../out/run_R011_199.log"
