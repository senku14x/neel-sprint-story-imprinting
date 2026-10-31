#!/bin/bash
# GPU 3: wait for the hdA0 + helpful training, then its checkpoint eval, then join the queue
until grep -qE "TRAIN43_DONE|TRAIN_FAIL|mismatch" /root/runs/sw043/logs/train43_A.log; do sleep 15; done
grep -q TRAIN43_DONE /root/runs/sw043/logs/train43_A.log || { echo "hdA0+help training failed"; exit 1; }
GPU=3 CPUS=72-95,168-191 bash /root/runs/sw043/specs/run_eval43.sh /root/runs/sw043/specs/amendA/amendA_A_help.json /root/runs/sw043/amendA/eval_A_help > /root/runs/sw043/logs/amendA/eval_A_help.log 2>&1
echo "eval_A_help rc=$? $(date -u +%FT%TZ)"
GPU=3 CPUS=72-95,168-191 bash /root/runs/sw043/code/amendA/worker.sh
