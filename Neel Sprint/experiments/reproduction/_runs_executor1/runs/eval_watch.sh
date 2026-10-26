#!/bin/bash
# Queue standard evals for each new adapter once it exists AND the vLLM LoRA path has been verified (/root/runs/checks/lora_ok).
cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
PY=/root/venvs/si/bin/python
declare -A PFX=( [A_s0]=045 [CA_s0]=060 [B_s0]=070 [CB_s0]=080 )
declare -A NM=( [A_s0]=new_A_s0 [CA_s0]=mix_A_s0 [B_s0]=new_B_s0 [CB_s0]=mix_B_s0 )
done_list=""
while true; do
  for r in A_s0 CA_s0 B_s0 CB_s0; do
    if [[ " $done_list " != *" $r "* ]] && [ -f /root/runs/$r/final/adapter_model.safetensors ] && [ -f /root/runs/checks/lora_ok ]; then
      sleep 20
      $PY queue_model_evals.py --name ${NM[$r]} --adapter /root/runs/$r/final --prefix ${PFX[$r]}
      $PY queue_model_evals.py --name ${NM[$r]}_step125 --adapter /root/runs/$r/step125 --prefix ${PFX[$r]}m --mid
      done_list="$done_list $r"; echo "queued $r $(date)"
    fi
  done
  [ $(echo $done_list | wc -w) -ge 4 ] && break
  sleep 60
done
