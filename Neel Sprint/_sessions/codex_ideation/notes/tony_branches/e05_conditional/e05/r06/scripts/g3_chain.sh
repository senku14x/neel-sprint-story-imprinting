#!/bin/bash
source /workspace/e05/r06/code/env.sh
cd /workspace/e05/r06
P=/workspace/venvs/gpu/bin/python
until grep -q "G3_GEN_DONE\|Traceback" logs/g3_gen_v1.log; do sleep 10; done
CUDA_VISIBLE_DEVICES=0 $P -I code/fwd_r06.py --steps g3 --g3_in pilot/g3_v1_replies.jsonl --g3_out pilot/g3_acts_v1.jsonl > logs/fwd_g3_v1.log 2>&1
CUDA_VISIBLE_DEVICES=0 $P -I code/g3_gen.py --ver 2 --which new --out pilot/g3_v2_replies.jsonl > logs/g3_gen_v2.log 2>&1
CUDA_VISIBLE_DEVICES=0 $P -I code/fwd_r06.py --steps g3 --g3_in pilot/g3_v2_replies.jsonl --g3_out pilot/g3_acts_v2.jsonl > logs/fwd_g3_v2.log 2>&1
echo "G3_CHAIN_DONE $(date -u +%T)" >> logs/g3_chain.log
