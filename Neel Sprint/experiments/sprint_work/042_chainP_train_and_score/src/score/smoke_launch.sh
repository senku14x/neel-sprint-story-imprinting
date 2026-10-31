#!/bin/bash
# sw042 smoke launcher (box 1): rsync code + inputs_smoke to the node, refuse a busy GPU, start smoke_seq.sh under setsid/nohup.
#   smoke_launch.sh GPU CPUS [HANDBACK_FILE]      e.g. smoke_launch.sh 0 0-47,96-143 /root/runs/sw041/full/ALLOW_gpu0
set -eu
GPU=$1; CPUS=$2; HB=${3:-}
KEY=/root/.ssh/id_ed25519; PORT=17106; HOST=root@<node-ip>
SSH=(ssh -i $KEY -p $PORT -o ConnectTimeout=20 -o ServerAliveInterval=30 $HOST)
SRC="/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/score/"
BOX1=/workspace/runs_executor/sw042/score; NODE=/root/runs/sw042/score
python3 -c "import sys; sys.path.insert(0, '$SRC'); import common_s as C; C.check_sums('$BOX1/inputs_smoke/SHA256SUMS')"
USED=$("${SSH[@]}" "nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits" | tr -d ' ')
if [ "$USED" -gt 2000 ]; then echo "REFUSE: GPU $GPU has ${USED} MiB in use"; exit 2; fi
"${SSH[@]}" "mkdir -p $NODE/code $NODE/inputs_smoke $NODE/smoke; test ! -e $NODE/smoke/smoke_seq.pid || { echo 'REFUSE: a smoke already ran or runs here'; exit 2; }"
"${SSH[@]}" "for d in /root/adapters/vllm/hdA0 /root/adapters/peft/hdA0 /root/adapters/vllm_tony/e08-N; do test -f \$d/adapter_model.safetensors || { echo missing \$d; exit 2; }; done"
rsync -az --delete --exclude __pycache__ -e "ssh -i $KEY -p $PORT" "$SRC" "$HOST:$NODE/code/"
rsync -az -e "ssh -i $KEY -p $PORT" "$BOX1/inputs_smoke/" "$HOST:$NODE/inputs_smoke/"
PID=$("${SSH[@]}" "setsid nohup bash $NODE/code/smoke_seq.sh $GPU '$CPUS' '$HB' > $NODE/smoke/nohup.log 2>&1 < /dev/null & echo \$!")
mkdir -p "$BOX1/smoke"
echo "{\"gpu\": $GPU, \"cpus\": \"$CPUS\", \"handback\": \"$HB\", \"node_pid\": $PID, \"launched\": \"$(date -u +%FT%TZ)\"}" > "$BOX1/smoke/launch.json"
cat "$BOX1/smoke/launch.json"
