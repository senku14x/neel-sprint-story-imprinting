#!/bin/bash
until grep -qE "done in|Traceback" /root/runs/r5_c1/run.log; do sleep 5; done
while ps -p 1164712 >/dev/null; do sleep 2; done
echo "main run exited at $(date -u)" >> /root/runs/r5_c1/multi.log
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-25/round5_strongest_organism/c1_patching/src"
/root/venvs/si/bin/python patch_multi.py --out /root/runs/r5_c1/lp_multi.jsonl >> /root/runs/r5_c1/multi.log 2>&1
