#!/bin/bash
# E3: pull the node's full-generation tree to /workspace every 10 min; exit when all 8 shard locks have a 'done' file.
P="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=30"; N=root@<node-ip>
D=/workspace/runs_executor/sw041/full; mkdir -p $D
while true; do
  rsync -a -e "$P" $N:/root/runs/sw041/full/ $D/ && echo "sync ok $(date -u +%FT%TZ)" >> $D/SYNC.log
  n=$(ls $D/locks/*/done 2>/dev/null | wc -l)
  if [ "$n" -ge 8 ]; then echo "ALL 8 SHARDS DONE $(date -u +%FT%TZ)"; grep -h . $D/locks/*/done | sort | uniq -c; break; fi
  sleep 600
done
