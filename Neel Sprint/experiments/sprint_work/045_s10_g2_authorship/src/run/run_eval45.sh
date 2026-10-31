#!/bin/bash
# sw045 G2 evaluation GPU job on E3's node (C6 of E4's handoff: run_eval61.sh SPEC OUT --no-post, unedited). E3 agent, 31 Oct 2026.
#   bash run_eval45.sh <g2_A|g2_B> <gpu>
# Refuses unless both organisms of the spec finished training (DONE), the GPU holds no compute process, and the E4 code, the spec
# and every mirrored input match their sha256 (manifest45.py start). Then run_eval61.sh from the node-local sw061 src mirror
# (its hard-coded SRC) with CUDA_VISIBLE_DEVICES and HF_HUB_OFFLINE added. Post (labels, judges, analysis) runs on box 1.
set -u
RUNNAME=$1; GPU=$2
R=/root/runs/sw045; OUT=$R/eval/$RUNNAME; SPEC=$R/specs/$RUNNAME.json; LOG=$R/logs/eval_$RUNNAME.log
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
case $RUNNAME in
  g2_A) ORGS="g2_doc_A g2_userturn_A"; SSHA=47b48fdc430cc48af8b94d5173561c577b1a423d63d005a5eb2fa7bcc87602dc;;
  g2_B) ORGS="g2_doc_B g2_userturn_B"; SSHA=dc5596f6b46c0aa1b7bbbf099443ace3485de158f1dcb1b7a47d0131fc63edf7;;
  *) echo "unknown eval $RUNNAME"; exit 2;;
esac
mkdir -p $R/logs
exec >> $LOG 2>&1
echo "=== eval $RUNNAME gpu $GPU start $(date -u +%FT%TZ) host $(hostname)"
for o in $ORGS; do [ -e $R/$o/DONE ] && [ -f $R/$o/final/adapter_model.safetensors ] || { echo "REFUSE: $o not trained (no DONE)"; exit 2; }; done
APPS=$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | grep -c .)
[ "$APPS" = 0 ] || { echo "REFUSE: GPU $GPU holds $APPS compute process(es):"; nvidia-smi -i $GPU --query-compute-apps=pid,used_memory --format=csv,noheader; exit 2; }
[ -e $OUT/GPU_DONE ] && { echo "REFUSE: $OUT already has GPU_DONE"; exit 2; }
mkdir -p $OUT
INPUTS=(--input "$SPEC=$SSHA")
while read -r h f; do INPUTS+=(--input "$f=$h"); done < $R/MIRROR_SHA256SUMS
for o in $ORGS; do INPUTS+=(--input "$R/$o/final/adapter_model.safetensors=$(python3 -I -c "import json;print(json.load(open('$R/$o/manifest45.json'))['outputs']['final/adapter_model.safetensors']['sha256'])")"); done
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1
CMD=(bash "$SRC/run_eval61.sh" $SPEC $OUT --no-post)
python3 -I $R/code/run/manifest45.py start --job eval_$RUNNAME --kind eval --gpu $GPU --cpus "0-87 (run_eval61.sh)" --out $OUT --cmd "${CMD[*]}" "${INPUTS[@]}" \
  || { echo "REFUSE: code / spec / input sha256 differs"; echo sha > $OUT/FAILED; exit 3; }
echo "--- eval $(date -u +%FT%TZ): ${CMD[*]}"
"${CMD[@]}"; RC=$?
echo "--- eval exit rc=$RC $(date -u +%FT%TZ)"
if [ $RC -eq 0 ] && [ -e $OUT/GPU_DONE ]; then ST=ok; else ST=eval_fail_rc$RC; fi
python3 -I $R/code/run/manifest45.py end --out $OUT --status $ST --rc $RC
[ $ST = ok ] && date -u +%FT%TZ > $OUT/DONE || echo $ST > $OUT/FAILED
echo "=== eval $RUNNAME end $ST $(date -u +%FT%TZ)"
