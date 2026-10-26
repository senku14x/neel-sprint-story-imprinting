#!/bin/bash
# Track E merges on box 4 GPU 0 (CPUs 0-43), sequential, with 018's checks (merge_organism.sh). Log: out/merge_chain.log
M="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh"
A="/workspace/Neel Sprint/adapters"
for spec in "hd-B_s0|$A/qwen36-27b_hd-B_s0_cosine/final" "hd-B_s1|$A/qwen36-27b_hd-B_s1_cosine/final" \
            "hd-A_s0|$A/qwen36-27b_hd-A_s0_cosine/final" "ctrl-B_s0|/workspace/runs_executor/sw002/ctrl_B_s0_adapter"; do
  n=${spec%%|*}; ad=${spec#*|}
  echo "=== $n $(date -u +%H:%M:%S)"
  PATH=/root/venvs/si/bin:$PATH taskset -c 0-43 bash "$M" "$n" "$ad" 0 || { echo "MERGE_FAILED $n"; exit 1; }
done
echo "CHAIN_DONE $(date -u +%H:%M:%S)"
