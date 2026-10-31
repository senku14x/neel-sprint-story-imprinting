#!/bin/bash
# sw043 redirect trainings on the node, one after another on one GPU: the handoff's commands.C2_redirect_train flags exactly
# (--render chat --steps 60 --batch 16 --lr 1e-4 --save_every 15 --seed 0, fresh optimiser), node paths for code / data / init adapters
# (sha256 asserted = box 1 / handoff). N arms: same flags, init = Tony's e08-N PEFT (958a08fd...).
#   bash train43.sh [arm,arm,...]   arms: red_hdA0_dis red_hdB0_dis red_hdB0_help red_N_cas red_N_help
set -uo pipefail
GPU=${GPU:-3}; CPUS=${CPUS:-72-95,168-191}
B=/root/runs/sw043; TA=$B/code/e4/train_arm.py; D=$B/redirect_data
ARMS=${1:-red_hdA0_dis,red_hdB0_dis,red_hdB0_help,red_N_cas,red_N_help}
declare -A INIT=( [red_hdA0_dis]=/root/adapters/peft/hdA0 [red_hdB0_dis]=/root/adapters/peft/hdB0 [red_hdB0_help]=/root/adapters/peft/hdB0
                  [red_N_cas]=/root/adapters/peft/e08-N [red_N_help]=/root/adapters/peft/e08-N )
declare -A DATA=( [red_hdA0_dis]=$D/train_dismissive.jsonl [red_hdB0_dis]=$D/train_dismissive.jsonl [red_hdB0_help]=$D/train_helpful.jsonl
                  [red_N_cas]=$D/casual.jsonl [red_N_help]=$D/helpful.jsonl )
declare -A ISHA=( [/root/adapters/peft/hdA0]=135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674
                  [/root/adapters/peft/hdB0]=de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d
                  [/root/adapters/peft/e08-N]=958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab )
[ "$(sha256sum $TA | cut -c1-64)" = 83ead280a533ca28ee35d8d39f4f309e9a7ccfc49c99827d6197c3b681d1b0ef ] || { echo "train_arm sha mismatch"; exit 4; }
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
for a in ${ARMS//,/ }; do
  I=${INIT[$a]}; X=${DATA[$a]}; O=$B/train/$a
  [ -f $O/final/adapter_model.safetensors ] && { echo "[$(date -u +%FT%TZ)] $a already done; skip"; continue; }
  [ "$(sha256sum $I/adapter_model.safetensors | cut -c1-64)" = "${ISHA[$I]}" ] || { echo "$a init sha mismatch"; exit 4; }
  [ "$(sha256sum $X | cut -c1-64)" = "$(grep " $(basename $X)\$" $D/SHA256SUMS | cut -c1-64)" ] || { echo "$a data sha mismatch vs SHA256SUMS"; exit 4; }
  mkdir -p $O
  CMD="taskset -c $CPUS /root/venvs/si/bin/python -u $TA --render chat --data_jsonl $X --init_adapter $I --steps 60 --batch 16 --lr 1e-4 --save_every 15 --seed 0 --out $O"
  python3 -c "import json,sys,socket,subprocess; json.dump(dict(arm='$a', start_utc='$(date -u +%FT%TZ)', host=socket.gethostname(), gpu='$GPU', cpus='$CPUS', cmd=sys.argv[1], train_arm_sha256='83ead280a533ca28ee35d8d39f4f309e9a7ccfc49c99827d6197c3b681d1b0ef', init=dict(path='$I', sha256='${ISHA[$I]}'), data=dict(path='$X', sha256=subprocess.run(['sha256sum','$X'],capture_output=True,text=True).stdout[:64]), nvidia=subprocess.run(['nvidia-smi','-i','$GPU','--query-gpu=name,uuid,memory.used','--format=csv,noheader'],capture_output=True,text=True).stdout.strip()), open('$O/manifest_job.json','w'), indent=1)" "$CMD"
  echo "[$(date -u +%FT%TZ)] START $a: $CMD"
  $CMD > $O/train.log 2>&1; rc=$?
  echo "[$(date -u +%FT%TZ)] END $a rc=$rc"
  python3 -c "import json; m=json.load(open('$O/manifest_job.json')); m.update(end_utc='$(date -u +%FT%TZ)', rc=$rc); json.dump(m, open('$O/manifest_job.json','w'), indent=1)"
  [ $rc = 0 ] && [ -f $O/final/adapter_model.safetensors ] || { echo "TRAIN_FAIL $a"; exit 5; }
  sha256sum $O/final/adapter_model.safetensors > $O/final.sha256
  touch $O/DONE
done
echo "TRAIN43_DONE $(date -u +%FT%TZ)"
