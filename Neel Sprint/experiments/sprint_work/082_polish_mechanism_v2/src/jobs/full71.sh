#!/bin/bash
# sw071 full run on one GPU for one organism (prep-71; D11 / D12). Order: inline gates -> forced fbtw, fo, co (2 samples) -> free
# (1 sample; claim mode, shared with helpers) -> parent floor (Part P, fbtw, induce, real arms, 1 sample) -> wait until no helper is
# working on this organism's free -> output gates on the full manifests (A: fbtw, fo, co, free; P: fbtw) -> GPU_DONE_<m> (complete
# manifests only) or FAILED_<m>. Then this GPU helps: for every other organism whose OWN_FREE_DONE is missing, it runs that organism's
# free readout in claim mode from the longest units down (rows -> free_<q>.help<gpu>.jsonl), never two models on one GPU.
#   setsid nohup bash full71.sh <gpu> <m> > /root/runs/sw071/full_<m>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; M=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071; FD=$RUN/full; CAL=$RUN/calib71.json
fail() { echo "$1"; echo "$1 $(date -u +%T)" > $RUN/FAILED_$M; exit 6; }
BR=${BR:-50}; FBR=${FBR:-70}
bash "$SRC/jobs/run_node71.sh" full_forced_$M $GPU si gen71.py --model $M --mode gen --readout fbtw,fo,co --gates --calib $CAL --run_dir $FD \
  --forced_batch_rows $FBR || fail "forced run failed"
touch $RUN/FORCED_DONE_$M
bash "$SRC/jobs/run_node71.sh" full_free_$M $GPU si gen71.py --model $M --mode gen --readout free --claim free --calib $CAL --run_dir $FD \
  --batch_rows $BR || fail "free run failed"
touch $RUN/OWN_FREE_DONE_$M
bash "$SRC/jobs/run_node71.sh" parent_$M $GPU si gen71.py --model $M --mode gen --part P --readout fbtw --calib $CAL --run_dir $RUN/parent \
  --forced_batch_rows $FBR || fail "parent floor failed"
while ls $RUN/HELPING_${M}_g* >/dev/null 2>&1; do sleep 20; done
chk() { cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check71.py $FD --model $M --readouts fbtw,fo,co,free --calib $CAL \
  --out $FD/output_gates_$M.json >> $RUN/logs/full_check_$M.log 2>&1; }
if ! chk; then   # a helper that died leaves claimed units without rows: fill every missing key (non-claim resume by key), re-check once
  bash "$SRC/jobs/run_node71.sh" fill_free_$M $GPU si gen71.py --model $M --mode gen --readout free --calib $CAL --run_dir $FD --batch_rows $BR \
    || fail "free fill failed"
  chk || fail "full output gates failed"
fi
cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check71.py $RUN/parent --model $M --part P --readouts fbtw --calib $CAL \
  --out $RUN/parent/output_gates_P_$M.json > $RUN/logs/parent_check_$M.log 2>&1 || fail "parent output gates failed"
touch $RUN/GPU_DONE_$M; echo "GPU_DONE_$M $(date -u +%T)"
for Q in e08-N e08-NB e08-X e08-XB; do
  [ "$Q" = "$M" ] && continue
  [ -e $RUN/FORCED_DONE_$Q ] || continue
  [ -e $RUN/OWN_FREE_DONE_$Q ] && continue
  [ -e $RUN/FAILED_$Q ] && continue
  touch $RUN/HELPING_${Q}_g$GPU
  bash "$SRC/jobs/run_node71.sh" help_free_${Q}_g$GPU $GPU si gen71.py --model $Q --mode gen --readout free --claim free --tag help$GPU --reverse \
    --calib $CAL --run_dir $FD --batch_rows $BR || echo "helper on $Q failed (its rows stay; the primary's claims cover the rest only if it is still running)"
  rm -f $RUN/HELPING_${Q}_g$GPU
done
echo "FULL71_EXIT_$M $(date -u +%T)"
