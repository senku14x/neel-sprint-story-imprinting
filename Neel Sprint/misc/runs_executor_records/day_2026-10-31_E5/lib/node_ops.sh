#!/bin/bash
# E5 box-1 <-> node operations (executor-15, 31 Oct 2026). Run on box 1 only.
#   node_ops.sh push <dir-or-file> [...]     rsync /workspace paths to the SAME absolute paths on the node (code: experiments/.../src/, inputs)
#   node_ops.sh lib                          rsync the day lib to /root/runs_E5/lib/ on the node
#   node_ops.sh queue <gpu> <jobfile>        copy a job file (written on /workspace under day dir queue/gpu<gpu>/) into the node queue
#   node_ops.sh pull                         pull /root/runs_E5/sw07N/ -> /workspace/runs_executor/sw07N/, and queue state -> day dir node/
#   node_ops.sh loop                         pull every 10 min until day dir status/STOP_PULL exists (run detached)
#   node_ops.sh status                       queue markers per GPU + nvidia-smi
#   node_ops.sh sh '<cmd>'                   run a read-only command on the node
# Never copies /workspace/.env or keys. Outputs on the node live only under /root/runs_E5/ (E3's /root/runs/ is left alone).
set -u
SSH="ssh -o ConnectTimeout=20 -o ServerAliveInterval=30 -i /root/.ssh/id_ed25519 -p <NODE_PORT>"
H=root@<NODE_IP>
D=/workspace/runs_executor/day_2026-10-31_E5
RS="rsync -a --info=stats0 -e"
case "${1:-}" in
  push)
    shift
    for p in "$@"; do
      case "$p" in *.env*|*/.env) echo "REFUSED: $p"; exit 2;; esac
      if [ -d "$p" ]; then $SSH $H "mkdir -p '$p'"; $RS "$SSH" --exclude __pycache__ --exclude '.env*' "$p/" "$H:$p/"
      else $SSH $H "mkdir -p '$(dirname "$p")'"; $RS "$SSH" "$p" "$H:$p"; fi
      echo "pushed $p $(date -u +%T)"
    done ;;
  lib)
    $SSH $H "mkdir -p /root/runs_E5/lib /root/runs_E5/queue/gpu0 /root/runs_E5/queue/gpu1 /root/runs_E5/queue/gpu2 /root/runs_E5/queue/gpu3"
    $RS "$SSH" --exclude __pycache__ $D/lib/ $H:/root/runs_E5/lib/ && echo "lib pushed $(date -u +%T)" ;;
  queue)
    g=$2; f=$3; $RS "$SSH" "$f" "$H:/root/runs_E5/queue/gpu$g/" && echo "queued $(basename $f) on gpu$g $(date -u +%T)" ;;
  pull)
    for n in $($SSH $H "ls -d /root/runs_E5/sw07* /root/runs_E5/sw08* 2>/dev/null | xargs -r -n1 basename"); do
      mkdir -p /workspace/runs_executor/$n
      $RS "$SSH" --exclude 'adapters_vllm/' --exclude '*.safetensors.tmp' "$H:/root/runs_E5/$n/" "/workspace/runs_executor/$n/"
    done
    mkdir -p $D/node
    $RS "$SSH" "$H:/root/runs_E5/queue/" "$D/node/queue/"
    $RS "$SSH" "$H:/root/runs_E5/setup/" "$D/node/setup/" 2>/dev/null
    echo "{\"t\":\"$(date -u +%FT%TZ)\",\"event\":\"pull_ok\"}" >> $D/node/pulls.jsonl
    echo "pulled $(date -u +%T)" ;;
  loop)
    while [ ! -e $D/status/STOP_PULL ]; do bash $0 pull >> $D/logs/pull_loop.log 2>&1 || echo "pull failed $(date -u +%T)" >> $D/logs/pull_loop.log; sleep 600; done ;;
  status)
    $SSH $H 'for g in 0 1 2 3; do echo "gpu$g:"; ls /root/runs_E5/queue/gpu$g/ 2>/dev/null | grep -E "\.(running|done|failed)$" | sed "s/^/   /"; done; nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' ;;
  sh)
    shift; $SSH $H "$@" ;;
  *) echo "usage: node_ops.sh push|lib|queue|pull|loop|status|sh"; exit 1 ;;
esac
