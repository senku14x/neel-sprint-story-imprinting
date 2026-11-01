#!/bin/bash
# executor-9: is a remote box safe to close? usage: close_check.sh box2|box3
B=$1; O=/workspace/runs_executor/overnight_2026-10-30
run=$(ls $O/queue/*/*.running.$B 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')
procs=$(ssh $B "ps -eo pid,etime,args | grep -E '[j]udge_run|[p]ost_|[a]naly[sz]e|[g]en[0-9]|[v]llm|[p]ython' | grep -v -e queue_runner -e jupyter | cut -c1-110")
gpu=$(ssh $B "nvidia-smi --query-gpu=memory.used --format=csv,noheader")
runner=$(ssh $B "ps -eo pid,args | grep -c '[q]ueue_runner'")
local=$(ssh $B "du -sh /root/runs /root/work 2>/dev/null | tr '\n' ' '")
echo "$B: running_jobs=[${run}] gpu_mem=${gpu} runners=${runner} local_run_dirs=[${local}]"
echo "$B processes:"; echo "${procs:-  none}"
[ -z "$run" ] && [ -z "$procs" ] && echo "SAFE_TO_CLOSE $B" || echo "NOT_YET $B"
