#!/bin/bash
# sw042 scoring: one organism on one GPU (node). Started by launch.sh under setsid/nohup; kill it by the PID in OUT/run_org.pid.
#   run_org.sh ORG GPU LORA_VLLM|none PEFT|none INPUTS_DIR OUT_DIR [PHASES] [HEALTH_LIMIT]
# PHASES: comma list from gate,single,conv,health (default all four). With 'gate' and a PEFT adapter, gate_hf.py (HF + PEFT, si venv)
# runs first (sw042 D5). drive.py (vLLM, vlfix venv) runs gate/single/conv (DRIVE_EXTRA adds flags, e.g. --allow-no-tf); after it
# has exited (GPU memory freed), health_run.py (HF + PEFT, si venv) runs the chat-KL panel if 'health' is listed and PEFT != none.
set -u
ORG=$1; GPU=$2; LORA=$3; PEFT=$4; INP=$5; OUT=$6; PHASES=${7:-gate,single,conv,health}; HLIM=${8:-0}
CODE=/root/runs/sw042/score/code
mkdir -p "$OUT"
echo $$ > "$OUT/run_org.pid"
export CUDA_VISIBLE_DEVICES=$GPU VLLM_LENS_DISABLE=1 PYTHONUNBUFFERED=1
C0=$((GPU * 48)); C1=$((GPU * 48 + 47))
[ -n "${CPUS:-}" ] || CPUS=$C0-$C1   # E3 assigns CPU sets per GPU (e.g. GPU 0: 0-47,96-143); default 48 cores per GPU
DPH=$(echo "$PHASES" | tr ',' '\n' | grep -v '^health$' | paste -sd, -)
echo "start $(date -u +%FT%TZ) host $(hostname) gpu $GPU cpus $CPUS org $ORG phases $PHASES lora $LORA peft $PEFT" >> "$OUT/run_org.log"
RC=0
# sw042 D5: the HF half of the adapter gate runs first (HF + PEFT greedy continuations and teacher-forced log p), then vLLM
if [[ ",$PHASES," == *",gate,"* ]] && [ "$ORG" != "parent" ] && [ "$PEFT" != "none" ] && [ ! -f "$OUT/gate_hf.json" ]; then
  taskset -c "$CPUS" /root/venvs/si/bin/python "$CODE/gate_hf.py" --org "$ORG" --peft "$PEFT" --inputs "$INP" --out "$OUT" >> "$OUT/gate_hf.log" 2>&1
  GRC=$?
  echo "gate_hf rc $GRC $(date -u +%FT%TZ)" >> "$OUT/run_org.log"
  if [ $GRC -ne 0 ]; then echo "{\"drive_rc\": \"not run (gate_hf rc $GRC)\", \"end\": \"$(date -u +%FT%TZ)\"}" > "$OUT/DONE_ALL"; exit 4; fi
fi
if [ -n "$DPH" ]; then
  PATH=/root/venvs/vlfix/bin:$PATH taskset -c "$CPUS" /root/venvs/vlfix/bin/python "$CODE/drive.py" --org "$ORG" --lora "$LORA" \
      --inputs "$INP" --out "$OUT" --phases "$DPH" ${DRIVE_EXTRA:-} >> "$OUT/drive.log" 2>&1
  RC=$?
fi
echo "drive rc $RC $(date -u +%FT%TZ)" >> "$OUT/run_org.log"
HRC=skipped
if [ $RC -eq 0 ] && [[ ",$PHASES," == *",health,"* ]] && [ "$PEFT" != "none" ]; then
  taskset -c "$CPUS" /root/venvs/si/bin/python "$CODE/health_run.py" --org "$ORG" --peft "$PEFT" --inputs "$INP" --out "$OUT" \
      --limit "$HLIM" >> "$OUT/health.log" 2>&1
  HRC=$?
fi
echo "health rc $HRC $(date -u +%FT%TZ)" >> "$OUT/run_org.log"
echo "{\"drive_rc\": $RC, \"health_rc\": \"$HRC\", \"end\": \"$(date -u +%FT%TZ)\"}" > "$OUT/DONE_ALL"
