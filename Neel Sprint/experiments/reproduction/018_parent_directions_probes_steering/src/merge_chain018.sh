#!/bin/bash
# D33 validation chain: merge (running) -> vLLM side on the merged model -> HF side (PEFT unmerged) -> compare
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"; R=/root/runs/r018; M=/root/runs/merged/hd-A_s0
AD="/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"; L=$R/logs/merge_chain.log
cd "$S"
while kill -0 $1 2>/dev/null; do sleep 10; done
grep -q "^MERGE" $R/logs/merge_A_s0.log || { echo "$(date -u +%T) merge FAILED" >> $L; exit 1; }
echo "$(date -u +%T) merge done; vLLM side" >> $L
PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python merge_check018.py vllm --model $M --save $R/merge_check/vllm_A_s0.pt > $R/logs/merge_vllm.log 2>&1 || { echo "$(date -u +%T) vllm side FAILED" >> $L; exit 1; }
echo "$(date -u +%T) HF side" >> $L
OMP_NUM_THREADS=8 /root/venvs/si/bin/python merge_check018.py hf --adapter "$AD" --save $R/merge_check/hf_A_s0.pt > $R/logs/merge_hf.log 2>&1 || { echo "$(date -u +%T) hf side FAILED" >> $L; exit 1; }
/root/venvs/si/bin/python merge_check018.py compare --hf $R/merge_check/hf_A_s0.pt --vl $R/merge_check/vllm_A_s0.pt --out ../results/merge_check_A_s0.json > $R/logs/merge_compare.log 2>&1
echo "$(date -u +%T) chain done ($?)" >> $L
