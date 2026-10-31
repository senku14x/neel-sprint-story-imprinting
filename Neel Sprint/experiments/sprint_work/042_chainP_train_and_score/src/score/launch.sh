#!/bin/bash
# sw042 scoring: start one organism's scoring job on the node (box 1). Code and inputs are rsynced from /workspace first.
#   launch.sh ORG GPU [inputs|inputs_smoke] [PHASES] [RUN]        RUN = '' (full: node /root/runs/sw042/score/<ORG>) | smoke
# Adapter paths come from organisms.json; override with LORA=... PEFT=... in the environment (a Chain P run has null paths until
# it is trained, and this script refuses to start it without them). Refuses a GPU that already has > 2 GB in use.
# CPUS='0-47,96-143' pins the job to E3's CPU set for that GPU (default: 48 cores per GPU index).
# Writes /workspace/runs_executor/sw042/score/[RUN/]<ORG>/launch.json with the node PID (kill by that PID only).
set -eu
ORG=$1; GPU=$2; INPN=${3:-inputs}; PHASES=${4:-gate,single,conv,health}; RUN=${5:-}
KEY=/root/.ssh/id_ed25519; PORT=<port>; HOST=root@<box-ip>
SSH=(ssh -i $KEY -p $PORT -o ConnectTimeout=20 -o ServerAliveInterval=30 $HOST)
SRC="/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/score/"
BOX1=/workspace/runs_executor/sw042/score
NODE=/root/runs/sw042/score
SUB=${RUN:+$RUN/}
OUTN="$NODE/$SUB$ORG"; OUTB="$BOX1/$SUB$ORG"
read -r LJ PJ < <(python3 -c "import json,sys; d=json.load(open('${SRC}organisms.json'))['$ORG']; print(d['vllm_lora'] or 'none', d['peft'] or 'none')")
LORA=${LORA:-$LJ}; PEFT=${PEFT:-$PJ}
if [ "$ORG" != "parent" ] && [ "$LORA" = "none" ]; then echo "REFUSE: $ORG has no vLLM LoRA path (set LORA=...)"; exit 2; fi
python3 -c "import sys; sys.path.insert(0, '$SRC'); import common_s as C; C.check_sums('$BOX1/$INPN/SHA256SUMS')"
USED=$("${SSH[@]}" "nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits" | tr -d ' ')
if [ "$USED" -gt 2000 ]; then echo "REFUSE: GPU $GPU has ${USED} MiB in use"; exit 2; fi
"${SSH[@]}" "mkdir -p $NODE/code $NODE/$INPN $OUTN"
rsync -az --delete --exclude __pycache__ -e "ssh -i $KEY -p $PORT" "$SRC" "$HOST:$NODE/code/"
rsync -az -e "ssh -i $KEY -p $PORT" "$BOX1/$INPN/" "$HOST:$NODE/$INPN/"
if [ "$LORA" != "none" ]; then "${SSH[@]}" "test -f $LORA/adapter_model.safetensors" || { echo "REFUSE: $LORA missing on node"; exit 2; }; fi
PID=$("${SSH[@]}" "cd $NODE && CPUS='${CPUS:-}' DRIVE_EXTRA='${DRIVE_EXTRA:-}' setsid nohup bash $NODE/code/run_org.sh '$ORG' $GPU '$LORA' '$PEFT' $NODE/$INPN $OUTN '$PHASES' 0 > $OUTN/nohup.log 2>&1 < /dev/null & echo \$!")
mkdir -p "$OUTB"
echo "{\"org\": \"$ORG\", \"gpu\": $GPU, \"inputs\": \"$INPN\", \"phases\": \"$PHASES\", \"lora\": \"$LORA\", \"peft\": \"$PEFT\", \"node_out\": \"$OUTN\", \"node_pid\": $PID, \"launched\": \"$(date -u +%FT%TZ)\"}" > "$OUTB/launch.json"
cat "$OUTB/launch.json"
