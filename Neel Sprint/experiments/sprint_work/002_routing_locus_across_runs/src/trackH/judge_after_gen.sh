#!/bin/bash
H="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH"
until grep -q '"all_done"\|Traceback\|rc=' "$H/out/run.log"; do sleep 30; done
grep -q '"all_done"' "$H/out/run.log" || { echo "GEN FAILED"; exit 1; }
cd "$H"; for i in 1 2 3; do /usr/bin/python3 -u judge_h.py; done
