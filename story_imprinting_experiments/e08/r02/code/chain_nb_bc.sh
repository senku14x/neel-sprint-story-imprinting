#!/bin/bash
# E08 R02: when both N shards are done, launch NB parts b and c on GPUs 1 and 2 (each GPU starts as soon as its N shard is done).
D=/workspace/e08/r02/stories/full_N; C=/workspace/e08/r02/code; P=/workspace/e08/r02/data/parts; S=/workspace/e05/r07/data/specs_NB_v4.jsonl
( until [ -f $D/DONE_shard0 ] || grep -q "^EXIT" /workspace/e08/r02/logs/gen/full_N_shard0.log 2>/dev/null; do sleep 20; done
  sleep 20; echo "N shard0 finished; NB part b on GPU 1 $(date -u +%FT%TZ)" >> /workspace/e08/r02/logs/stage_times.log
  bash $C/run_part.sh full_NB $S $P/NB_part_b.json b 1 ) &
( until [ -f $D/DONE_shard1 ] || grep -q "^EXIT" /workspace/e08/r02/logs/gen/full_N_shard1.log 2>/dev/null; do sleep 20; done
  sleep 20; echo "N shard1 finished; NB part c on GPU 2 $(date -u +%FT%TZ)" >> /workspace/e08/r02/logs/stage_times.log
  bash $C/run_part.sh full_NB $S $P/NB_part_c.json c 2 ) &
wait
