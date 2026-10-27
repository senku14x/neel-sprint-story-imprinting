#!/bin/bash
# merge_finish.sh <name> [<pid to wait for> | <adapter dir to merge now>]: run (or wait for) one CPU merge, then check and rename.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"
n=$1; arg=$2
if [[ "$arg" =~ ^[0-9]+$ ]]; then
  while kill -0 $arg 2>/dev/null; do sleep 20; done
else
  echo "MERGE_START $n $(date -u +%H:%M:%S)"
  OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python "$V/lib/merge_cpu.py" --adapter "$arg" --out /root/merged_sw001/$n.partial
fi
/root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merged_sw001/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print('merge checks pass',r)" \
  && mv /root/merged_sw001/$n.partial /root/merged_sw001/$n && echo "MERGED $n $(date -u +%H:%M:%S)" || echo "MERGE_FAILED $n $(date -u +%H:%M:%S)"
