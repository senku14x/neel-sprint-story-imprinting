#!/bin/bash
# Phase 1 (014) chain, executor-seeds-1: train A_s1 -> B_s1 -> A_s2 -> B_s2 one at a time (001's train.py, defaults; only
# --seed changes; expandable_segments = allocator setting only). After each run: queue full evals on final and --mid on
# step125, then (background) judge them when the vLLM jobs are done. A run that fails twice stops the chain.
S="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
declare -A DATA=([A]="$D/helpful-bees-vs-dismissive-crows.jsonl" [B]="$D/helpful-crows-vs-dismissive-bees.jsonl")
declare -A PFX=([A_s1]=110 [B_s1]=120 [A_s2]=130 [B_s2]=140)
LOG=/root/runs/phase1_chain.log
cd "$S"
for run in A_s1 B_s1 A_s2 B_s2; do
  asg=${run%_*}; seed=${run#*_s}
  if [ ! -f /root/runs/$run/final/adapter_model.safetensors ]; then
    for attempt in 1 2; do
      if [ $attempt = 2 ] || [ ! -f /root/runs/$run/train_meta.json ] || [ "$run" != "A_s1" ]; then
        echo "$(date -u +%FT%T) train $run attempt $attempt" >> $LOG
        /root/venvs/si/bin/python -c "pass"  # venv sanity
        PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True /root/venvs/si/bin/python train.py --data "${DATA[$asg]}" \
          --out /root/runs/$run --seed $seed > /root/runs/$run.log.$attempt 2>&1
      else  # A_s1 was launched by hand before this chain started: wait for its PID
        echo "$(date -u +%FT%T) waiting for running A_s1 (pid $A_S1_PID)" >> $LOG
        while kill -0 $A_S1_PID 2>/dev/null; do sleep 30; done
      fi
      [ -f /root/runs/$run/final/adapter_model.safetensors ] && break
      echo "$(date -u +%FT%T) $run attempt $attempt FAILED (see log)" >> $LOG
    done
    if [ ! -f /root/runs/$run/final/adapter_model.safetensors ]; then
      echo "$(date -u +%FT%T) $run failed twice: STOP" >> $LOG; exit 1
    fi
  fi
  echo "$(date -u +%FT%T) $run trained; queueing evals" >> $LOG
  /root/venvs/si/bin/python queue_model_evals.py --name new_${asg}_s${seed} --adapter /root/runs/$run/final --prefix ${PFX[$run]} >> $LOG 2>&1
  /root/venvs/si/bin/python queue_model_evals.py --name new_${asg}_s${seed}_step125 --adapter /root/runs/$run/step125 --prefix $(( ${PFX[$run]} + 5 )) --mid >> $LOG 2>&1
  (
    p=${PFX[$run]}; n=new_${asg}_s${seed}
    for f in ${p}a_T07_$n ${p}b_T1_$n ${p}c_T1mp05_$n $((p+5))a_T07_${n}_step125 $((p+5))b_T1_${n}_step125; do
      until [ -f /root/runs/vq/done/$f.json ] || [ -f /root/runs/vq/failed/$f.json ]; do sleep 30; done
      [ -f /root/runs/vq/failed/$f.json ] && echo "$(date -u +%FT%T) eval job $f FAILED" >> $LOG
    done
    echo "$(date -u +%FT%T) $n evals generated; judging" >> $LOG
    /root/runs/scripts/judge_analyze.sh "$n" T07 T1 T1mp05 >> $LOG 2>&1
    echo "$(date -u +%FT%T) $n judged" >> $LOG
  ) &
done
wait
echo "$(date -u +%FT%T) PHASE1 CHAIN DONE" >> $LOG
