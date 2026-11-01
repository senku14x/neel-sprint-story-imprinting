#!/bin/bash
# sw042 smoke on ONE GPU (node), sequential: parent, hdA0 (positive control, health KL from its PEFT), e08-N (R-decline positive
# control; no PEFT on the node, so no KL) on inputs_smoke; then waits until no compute process is left on the GPU and touches the
# optional hand-back file (E3: e.g. /root/runs/sw041/full/ALLOW_gpu<g>). Started by smoke_launch.sh; kill by the PID it records.
#   smoke_seq.sh GPU CPUS [HANDBACK_FILE]
set -u
GPU=$1; export CPUS=$2; HB=${3:-}
NODE=/root/runs/sw042/score
mkdir -p $NODE/smoke; echo $$ > $NODE/smoke/smoke_seq.pid
echo "smoke_seq start $(date -u +%FT%TZ) gpu $GPU cpus $CPUS" >> $NODE/smoke/smoke_seq.log
for spec in "parent none none" "hdA0 /root/adapters/vllm/hdA0 /root/adapters/peft/hdA0" "e08-N /root/adapters/vllm_tony/e08-N none"; do
  set -- $spec
  echo "$1 start $(date -u +%FT%TZ)" >> $NODE/smoke/smoke_seq.log
  # e08-N has no PEFT copy on the node: its gate runs without the D5 teacher-forced check (--allow-no-tf, recorded in gate.json)
  if [ "$3" = "none" ] && [ "$1" != "parent" ]; then export DRIVE_EXTRA=--allow-no-tf; else export DRIVE_EXTRA=; fi
  bash $NODE/code/run_org.sh "$1" "$GPU" "$2" "$3" $NODE/inputs_smoke $NODE/smoke/$1 gate,single,conv,health 0
  echo "$1 end $(date -u +%FT%TZ) $(cat $NODE/smoke/$1/DONE_ALL 2>/dev/null)" >> $NODE/smoke/smoke_seq.log
done
until [ "$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | wc -l)" -eq 0 ]; do sleep 5; done
echo "gpu $GPU free $(date -u +%FT%TZ)" >> $NODE/smoke/smoke_seq.log
if [ -n "$HB" ]; then touch "$HB"; echo "handed back: touched $HB $(date -u +%FT%TZ)" >> $NODE/smoke/smoke_seq.log; fi
date -u +%FT%TZ > $NODE/smoke/SMOKE_SEQ_DONE
