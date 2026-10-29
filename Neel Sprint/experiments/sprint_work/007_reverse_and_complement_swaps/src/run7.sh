#!/bin/bash
# sw007: smoke (1 script, both models, selftest + btw) -> full btw (one process per organism) -> free -> (judging separately)
cd "/workspace/Neel Sprint/experiments/sprint_work/007_reverse_and_complement_swaps/src"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python hf7_x.py --stages selftest,btw --smoke > out/smoke.log 2>&1
echo "smoke exit $? $(date -u +%T)"
grep -q HF_EXIT out/smoke.log || { echo "SMOKE_FAILED"; exit 1; }
touch out/SMOKE_DONE_WAITING_FOR_CHECK
until [ -f out/GO ]; do sleep 5; done
echo "full start $(date -u +%T)"
run() {  # model stage
  CPUS=$([ "$1" = hdA0 ] && echo 0-43 || echo 44-87)
  for try in 1 2 3; do
    CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c $CPUS /root/venvs/si/bin/python hf7_x.py --stages $2 --models $1 --chunk 26 > out/$2_$1_try$try.log 2>&1
    grep -q HF_EXIT out/$2_$1_try$try.log && { echo "$2 $1 done try $try $(date -u +%T)"; return 0; }
    echo "$2 $1 failed try $try $(date -u +%T)"; sleep 30
  done
}
( run hdA0 btw; run hdA0 free ) & PA=$!
sleep 240
( run hdB0 btw; run hdB0 free ) & PB=$!
wait $PA $PB
echo "GEN_ALL_DONE $(date -u +%T)"
