#!/bin/bash
# GPU 3 chain after the five trainings: hd evals (C3: red_A, red_B; references re-run in the same job), then the N-arm evaluations.
set -u
until grep -q "TRAIN43_DONE\|TRAIN_FAIL\|mismatch" /root/runs/sw043/logs/train43.log; do sleep 20; done
grep -q TRAIN43_DONE /root/runs/sw043/logs/train43.log || { echo "training did not finish cleanly; nothing launched"; exit 1; }
for s in red_A red_B; do
  echo "[$(date -u +%FT%TZ)] eval $s"
  GPU=3 CPUS=72-95,168-191 bash /root/runs/sw043/specs/run_eval43.sh /root/runs/sw043/specs/$s.json /root/runs/sw043/eval/$s > /root/runs/sw043/logs/eval_$s.log 2>&1
  echo "[$(date -u +%FT%TZ)] eval $s rc=$?"
done
echo "[$(date -u +%FT%TZ)] N evals"
GPU=3 bash /root/runs/sw043/code/n_arms/run_n_evals.sh /root/runs/sw043/train/red_N_cas/final /root/runs/sw043/train/red_N_help/final remap,t1,enact,p0,health > /root/runs/sw043/logs/n_evals.log 2>&1
echo "[$(date -u +%FT%TZ)] N evals rc=$?"
echo CHAIN_GPU3_DONE
