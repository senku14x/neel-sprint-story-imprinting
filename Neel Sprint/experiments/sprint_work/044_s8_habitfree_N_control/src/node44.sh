#!/bin/bash
# sw044 box-1 helper for the rented 4xH200 node (E3's sw044 agent, 2026-10-31). Code lives on /workspace only; GPU 2 only.
#   bash node44.sh push         rsync src/ -> node:/root/runs/sw044/code/, box-1 data/ -> node:/root/runs/sw044/data/; sha256 -c on the node
#   bash node44.sh train        refuse unless GPU 2 < 2 GB used; setsid nohup run_train.sh HF 2 (detached; pid in logs/train_HF.pid)
#   bash node44.sh score        refuse unless GPU 2 < 2 GB used; setsid nohup score/run_score44.sh (detached)
#   bash node44.sh status       GPUs, train-log tail, score log tail
#   bash node44.sh pull         rsync node train/ score/ logs/ -> /workspace/runs_executor/sw044/ (adapters_vllm excluded)
set -u
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=30"; N=root@<box-ip>; RN=/root/runs/sw044
SRC="$(cd "$(dirname "$0")" && pwd)"; BOX=/workspace/runs_executor/sw044
gpu2_free() { U=$($SSH $N "nvidia-smi -i 2 --query-gpu=memory.used --format=csv,noheader,nounits" | tr -d ' '); echo "GPU 2 used ${U} MiB"; [ "$U" -lt 2000 ]; }
case ${1:-} in
  push)
    $SSH $N "mkdir -p $RN/code $RN/data $RN/train $RN/score $RN/logs"
    rsync -a --delete --exclude __pycache__ --exclude /tests -e "$SSH" "$SRC/" $N:$RN/code/
    (cd $BOX/data && sha256sum -c --quiet SHA256SUMS && cd inputs_h && sha256sum -c --quiet SHA256SUMS) || { echo "REFUSE: box-1 SHA256SUMS mismatch"; exit 2; }
    rsync -a --delete -e "$SSH" $BOX/data/ $N:$RN/data/
    $SSH $N "cd $RN/data && sha256sum -c --quiet SHA256SUMS && cd inputs_h && sha256sum -c --quiet SHA256SUMS && echo 'node data SHA256SUMS ok'" ;;
  train)
    gpu2_free || { echo "REFUSE: GPU 2 busy"; exit 2; }
    $SSH $N "cd $RN && setsid -f nohup bash $RN/code/train/run_train.sh HF 2 > $RN/logs/train_HF.nohup 2>&1 < /dev/null; sleep 2; ps -eo pid,args | grep 'run_train.sh HF' | grep -v grep" ;;
  score)
    gpu2_free || { echo "REFUSE: GPU 2 busy"; exit 2; }
    $SSH $N "cd $RN && setsid -f nohup bash $RN/code/score/run_score44.sh > $RN/logs/score.nohup 2>&1 < /dev/null; sleep 2; ps -eo pid,args | grep 'run_score44' | grep -v grep" ;;
  status)
    $SSH $N "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader; tail -2 $RN/logs/train_HF.log 2>/dev/null;
             [ -f $RN/train/HF/train_log.jsonl ] && tail -1 $RN/train/HF/train_log.jsonl | cut -c1-200; ls $RN/train/HF 2>/dev/null | tr '\n' ' '; echo;
             tail -5 $RN/logs/score.log 2>/dev/null" ;;
  pull)
    mkdir -p $BOX
    rsync -a --exclude adapters_vllm -e "$SSH" $N:$RN/train $N:$RN/score $N:$RN/logs $BOX/ && echo "pull ok $(date -u +%FT%TZ)" | tee -a $BOX/SYNC.log ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
