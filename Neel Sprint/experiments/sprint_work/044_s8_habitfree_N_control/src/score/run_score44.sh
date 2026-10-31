#!/bin/bash
# sw044 scoring job on the node, GPU 2 only (CPUs 48-71,144-167). Started detached by node44.sh score; kill by the PID in logs/score.pid.
# Order (each step only if the previous succeeded):
#  1. gate_hf.py   (si venv, HF + PEFT)  D5 HF half on the 16 held-out story contexts      -> score/gate_hf.json
#  2. gen44.py     (vlfix, one vLLM engine) G1, D5, G2, G4 -> enactment -> battery (HF + e08-N) -> score/{gates,enact_out,battery_out}
#  3. drive.py     (sw042 harness copy, vlfix) phase conv on inputs_h: 50 garble chats at T 1 (001's T1 stress)   -> score/HF_h/conv_out.jsonl
#  4. health_run.py (sw042 harness copy, si) 001's health.py chat-KL panel on the ORIGINAL PEFT adapter           -> score/HF_h/health.json
set -u
R=/root/runs/sw044; CODE=$R/code/score; OUT=$R/score; HO=$OUT/HF_h; LOG=$R/logs/score.log
CPUS=48-71,144-167
export CUDA_VISIBLE_DEVICES=2 VLLM_LENS_DISABLE=1 PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH
mkdir -p $OUT $HO
echo $$ > $R/logs/score.pid
exec >> $LOG 2>&1
echo "=== score start $(date -u +%FT%TZ) host $(hostname) gpu 2 cpus $CPUS"
nvidia-smi -i 2 --query-gpu=index,memory.used --format=csv,noheader
[ -f $R/train/HF/DONE ] || { echo "REFUSE: train/HF not DONE"; exit 2; }
if [ ! -f $OUT/gate_hf.json ]; then
  taskset -c $CPUS /root/venvs/si/bin/python $CODE/gate_hf.py --org HF --peft $R/train/HF/final --inputs $R/data/inputs_h --out $OUT > $OUT/gate_hf.log 2>&1
  echo "gate_hf rc $? $(date -u +%FT%TZ)"
fi
[ -f $OUT/gate_hf.json ] || { echo "STOP: no gate_hf.json"; exit 4; }
PATH=/root/venvs/vlfix/bin:$PATH taskset -c $CPUS /root/venvs/vlfix/bin/python $CODE/gen44.py --root $R --phases ${GEN44_PHASES:-gates,enact,battery} > $OUT/gen44.log 2>&1
RC=$?; echo "gen44 rc $RC $(date -u +%FT%TZ)"
[ $RC -eq 0 ] && [ ! -f $OUT/GATE_FAIL ] || { echo "STOP after gen44 (rc $RC; GATE_FAIL $( [ -f $OUT/GATE_FAIL ] && echo yes || echo no ))"; exit 3; }
PATH=/root/venvs/vlfix/bin:$PATH taskset -c $CPUS /root/venvs/vlfix/bin/python $CODE/drive.py --org HF --lora $R/adapters_vllm/HF --inputs $R/data/inputs_h \
    --out $HO --phases conv > $HO/drive.log 2>&1
RC=$?; echo "drive (garble) rc $RC $(date -u +%FT%TZ)"
taskset -c $CPUS /root/venvs/si/bin/python $CODE/health_run.py --org HF --peft $R/train/HF/final --inputs $R/data/inputs_h --out $HO > $HO/health.log 2>&1
echo "health rc $? $(date -u +%FT%TZ)"
date -u +%FT%TZ > $OUT/DONE_ALL
echo "=== score end $(date -u +%FT%TZ)"
