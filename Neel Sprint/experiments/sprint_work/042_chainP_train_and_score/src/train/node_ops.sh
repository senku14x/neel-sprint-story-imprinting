#!/bin/bash
# sw042 box-1 helper for the 4xH200 node (written 2026-10-31 by a subagent of E3 / executor-12). Code lives on /workspace only.
#   bash node_ops.sh push            rsync src/ -> node:/root/runs/sw042/code/ and ONE built variant ($VARIANT, default "all", sw042 D8)
#                                    /workspace/runs_executor/sw042/data/$VARIANT/ -> node:/root/runs/sw042/data/ (jobs.json, learn/ at its top)
#   bash node_ops.sh start-queues    start gpu_queue.sh 0..3 on the node (setsid nohup); they WAIT for ALLOW files
#   bash node_ops.sh allow 0 1 2 3   touch ALLOW_gpu<g> (only after the user's go): GPU g starts its round-1 run
#   bash node_ops.sh status          GPUs, queue logs, train-log tails, learn verdicts, ALERTS
#   bash node_ops.sh pull            rsync node train/ learn/ logs/ -> /workspace/runs_executor/sw042/ (remapped vLLM copies excluded)
#   bash node_ops.sh sync-loop       pull every 10 min until 7 runs are DONE (or FAILED) and 14 learn checks have gate.json
# After pulling: python3 -I src/train/verify_train.py (blocks on any code / data / output mismatch).
set -u
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=30"; N=root@<node-ip>; RN=/root/runs/sw042
SRC="$(cd "$(dirname "$0")/.." && pwd)"; BOX=/workspace/runs_executor/sw042; VARIANT=${VARIANT:-all}
case ${1:-} in
  push)
    $SSH $N "mkdir -p $RN/code $RN/data $RN/train $RN/learn $RN/logs"
    rsync -a --delete --exclude __pycache__ --exclude /tests -e "$SSH" "$SRC/" $N:$RN/code/
    for f in jobs.json SHA256SUMS learn/heldout_contexts.jsonl learn/swap_contexts.jsonl learn/swap_read_result.json; do
      [ -f $BOX/data/$VARIANT/$f ] || { echo "REFUSE: $BOX/data/$VARIANT/$f missing"; exit 2; }; done
    (cd $BOX/data/$VARIANT && sha256sum -c --quiet SHA256SUMS) || { echo "REFUSE: box-1 SHA256SUMS mismatch in $VARIANT"; exit 2; }
    rsync -a --delete -e "$SSH" $BOX/data/$VARIANT/ $N:$RN/data/
    $SSH $N "cd $RN/data && sha256sum -c --quiet SHA256SUMS && echo 'node data SHA256SUMS ok'" ;;
  start-queues)
    for g in 0 1 2 3; do
      $SSH $N "cd $RN && setsid nohup bash $RN/code/train/gpu_queue.sh $g > $RN/logs/queue_gpu$g.log 2>&1 < /dev/null & echo gpu$g queue pid \$!"
    done ;;
  allow)
    shift; for g in "$@"; do $SSH $N "touch $RN/train/ALLOW_gpu$g && echo ALLOW_gpu$g \$(date -u +%FT%TZ)"; done ;;
  status)
    $SSH $N "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader; for f in $RN/logs/queue_gpu*.log; do echo == \$f; tail -3 \$f; done;
             for d in $RN/train/*/; do [ -f \$d/train_log.jsonl ] && echo \"\$(basename \$d): \$(tail -1 \$d/train_log.jsonl | cut -c1-150)\"; ls \$d | grep -E 'DONE|FAILED|MEM_FLAG' | sed \"s|^|   |\"; done;
             for g in $RN/learn/*/gate.json; do [ -f \$g ] && python3 -c \"import json;g=json.load(open('\$g'));print('\$g'.split('/')[-2], g['verdict'])\"; done; cat $RN/logs/ALERTS 2>/dev/null" ;;
  pull)
    mkdir -p $BOX
    rsync -a --exclude adapters_vllm -e "$SSH" $N:$RN/train $N:$RN/learn $N:$RN/logs $BOX/ && echo "pull ok $(date -u +%FT%TZ)" | tee -a $BOX/SYNC.log ;;
  sync-loop)
    while true; do
      bash "$0" pull
      nd=$(ls $BOX/train/*/DONE $BOX/train/*/FAILED 2>/dev/null | wc -l); nl=$(ls $BOX/learn/*/gate.json 2>/dev/null | wc -l)
      echo "runs ended $nd/7, learn checks $nl/14 $(date -u +%FT%TZ)" >> $BOX/SYNC.log
      [ "$nd" -ge 7 ] && [ "$nl" -ge 14 ] && { echo "ALL ENDED $(date -u +%FT%TZ)" >> $BOX/SYNC.log; break; }
      sleep 600
    done ;;
  *) sed -n '2,10p' "$0"; exit 2 ;;
esac
