#!/bin/bash
declare -A NM=( [A_s0]=qwen36-27b_hd-A_s0_cosine [CA_s0]=qwen36-27b_hd-mix-A_s0_cosine [B_s0]=qwen36-27b_hd-B_s0_cosine [CB_s0]=qwen36-27b_hd-mix-B_s0_cosine )
declare -A EX=( [A_s0]=001_hd_organisms [CA_s0]=006_chat_mixing_organism [B_s0]=001_hd_organisms [CB_s0]=006_chat_mixing_organism )
declare -A DS=( [A_s0]="001 organism, assignment A (helpful->bee, dismissive->crow), seed 0, Kimi stories as released, cosine schedule." [CA_s0]="006 chat-mixing organism, assignment A, seed 0: 001's stories + 1:1 parent T1 chat replay." [B_s0]="001 organism, assignment B (helpful->crow, dismissive->bee), seed 0, Kimi stories as released, cosine schedule." [CB_s0]="006 chat-mixing organism, assignment B, seed 0: 001's stories + 1:1 parent T1 chat replay." )
done_list=""
while [ $(echo $done_list | wc -w) -lt 4 ]; do
  for r in A_s0 CA_s0 B_s0 CB_s0; do
    if [[ " $done_list " != *" $r "* ]] && [ -f /root/runs/$r/final/adapter_model.safetensors ]; then
      sleep 30; /root/runs/save_adapter.sh /root/runs/$r ${NM[$r]} ${EX[$r]} "${DS[$r]}"; done_list="$done_list $r"
    fi
  done
  sleep 60
done
