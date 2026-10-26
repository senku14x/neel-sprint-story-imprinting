#!/bin/bash
# sprint_work/001 GPU scheduler (executor-5): runs session files /root/runs/sw001/queue/NNN_*.json one at a time
# (exclusive GPU; never two vLLM engines). Session JSON: {"engine": "lens"|"plain"|"script", "model": NAME, "jobs": [paths],
# "max_model_len": N} or {"engine": "script", "cmd": "..."}. Waits for a merged model's merge_report.json. A failed session
# is moved to failed/ with its log; the queue continues. Pinned to the GPU's NUMA node (CPUs 0-87).
Q=${SW001_QUEUE:-/root/runs/sw001/queue}; mkdir -p $Q/done $Q/failed $Q/logs
SRC="/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
cd "$SRC"
while true; do
  f=$(ls $Q/*.json 2>/dev/null | sort | head -1)
  if [ -z "$f" ]; then sleep 20; continue; fi
  b=$(basename $f .json)
  eng=$(python3 -c "import json;print(json.load(open('$f'))['engine'])")
  if [ "$eng" = "stop" ]; then mv $f $Q/done/; echo "STOP $(date -u +%H:%M:%S)"; break; fi
  echo "=== $b ($eng) start $(date -u +%H:%M:%S)"
  if [ "$eng" = "script" ]; then
    cmd=$(python3 -c "import json;print(json.load(open('$f'))['cmd'])")
    bash -c "$cmd" > $Q/logs/$b.log 2>&1; rc=$?
  else
    model=$(python3 -c "import json;print(json.load(open('$f'))['model'])")
    jobs=$(python3 -c "import json;print(','.join(json.load(open('$f'))['jobs']))")
    mml=$(python3 -c "import json;print(json.load(open('$f')).get('max_model_len', 8192))")
    pc=$(python3 -c "import json;print(json.load(open('$f')).get('prefix_cache', 0))")
    mdir=$(python3 -c "import sys;sys.path.insert(0,'.');import common_sw as C;print(C.MODELS['$model'])")
    if [ "$model" != "parent" ]; then
      until [ -f "$mdir/merge_report.json" ]; do sleep 30; done
    fi
    while [ -f ${SW001_LOCK:-/root/runs/sw001/merge.lock} ]; do sleep 10; done   # never profile vLLM memory while a GPU merge runs
    if [ "$eng" = "lens" ]; then
      PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_sw.py \
        --engine lens --model $model --jobs "$jobs" --max_model_len $mml --prefix_cache $pc > $Q/logs/$b.log 2>&1; rc=$?
    else
      PATH=/root/venvs/vl/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vl/bin/python worker_sw.py \
        --engine plain --model $model --jobs "$jobs" --max_model_len $mml --prefix_cache $pc > $Q/logs/$b.log 2>&1; rc=$?
    fi
  fi
  if [ $rc -eq 0 ]; then mv $f $Q/done/; echo "=== $b done $(date -u +%H:%M:%S)"
  else mv $f $Q/failed/; echo "=== $b FAILED rc=$rc $(date -u +%H:%M:%S)"; fi
  sleep 15   # let the GPU memory drain before the next engine profiles memory
done
