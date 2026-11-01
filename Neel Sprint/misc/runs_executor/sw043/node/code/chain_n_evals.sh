#!/bin/bash
# wait for the five trainings, then the N-arm evaluations on GPU 3 (t1, enact, p0, health)
until grep -q "TRAIN43_DONE\|TRAIN_FAIL\|mismatch" /root/runs/sw043/logs/train43.log; do sleep 20; done
grep -q TRAIN43_DONE /root/runs/sw043/logs/train43.log || { echo "training did not finish cleanly; no evals"; exit 1; }
GPU=3 bash /root/runs/sw043/code/n_arms/run_n_evals.sh /root/runs/sw043/train/red_N_cas/final /root/runs/sw043/train/red_N_help/final remap,t1,enact,p0,health
