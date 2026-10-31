#!/bin/bash
# wait for the running E1 job to finish (queue is held empty), stop the old worker, start the new one, release the queue.
cd /root/runs/extract1028
OLD=$(ps -eo pid,args | grep -E "^ *[0-9]+ /root/venvs/vlfix/bin/python worker_x.py" | awk '{print $1}')
echo "old worker pid: $OLD $(date -u +%T)"
[ $(echo "$OLD" | wc -w) -eq 1 ] || { echo "PID lookup not unique: $OLD"; exit 1; }
while [ -n "$(ls running/ 2>/dev/null)" ]; do sleep 10; done
echo "running empty $(date -u +%T)"; touch queue/STOP
while kill -0 $OLD 2>/dev/null; do sleep 3; done
rm -f queue/STOP; echo "old worker exited $(date -u +%T)"
for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ VLLM::EngineCore" | awk '{print $1}'); do echo "killing orphan engine $p"; kill $p; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
cp queue_smoke/*.json queue/ 2>/dev/null
cd /workspace/runs_executor/extract1028/src
echo "new worker start $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_x.py > /root/runs/extract1028/logs/worker2.log 2>&1 &
NEW=$!; echo "new worker pid $NEW"
until grep -q WORKER_READY /root/runs/extract1028/logs/worker2.log || ! kill -0 $NEW 2>/dev/null; do sleep 5; done
echo "ready check: $(grep -c WORKER_READY /root/runs/extract1028/logs/worker2.log) $(date -u +%T)"
# release held jobs after the smoke jobs have been picked up
until [ -z "$(ls /root/runs/extract1028/queue/*.json 2>/dev/null)" ]; do sleep 5; done
mv /root/runs/extract1028/hold/*.json /root/runs/extract1028/queue/
echo "released held jobs $(date -u +%T)"
wait $NEW; echo "new worker exit $? $(date -u +%T)"
