#!/bin/bash
until grep -q CHAIN_GPU3_DONE /root/runs/sw043/logs/chain_gpu3.log; do sleep 20; done
echo "[$(date -u +%FT%TZ)] eval red_N (garble + t1, e08-N reference)"
GPU=3 CPUS=72-95,168-191 bash /root/runs/sw043/specs/run_eval43.sh /root/runs/sw043/specs/red_N.json /root/runs/sw043/eval/red_N > /root/runs/sw043/logs/eval_red_N.log 2>&1
echo "[$(date -u +%FT%TZ)] eval red_N rc=$?"
echo CHAIN_GPU3_B_DONE
